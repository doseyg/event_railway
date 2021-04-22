#!/usr/bin/python3
###  doseyg@r-networks.net 
###  September 2020
import os ## Used to get environment and web server variables
import cgi, cgitb ## used to get values from web forms
import datetime ## For timestamps in logging
import logging ## Implements logging
import getpass ## Used to get username from basic web authentication provided by Apache server
import uuid ## Used to generate unique connection ID for logs
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl
import atexit
import time ## for sleep delay
import glob ## Used to find all DHCP configuration files
import netaddr ## For picking an DHCP IP in subnet
import re ## used to search dhcp reservations for IP address in use
import subprocess ## Used to restart DHCP or scp DHCP file to remote server and use SSH to restart there

### Config variables ###
logfile='vm_manager.log'

user_config={}
config={}
### Add any admin user names here. 
user_config["admins"]=("admin","bob")
user_config["unknown_user"]={}
###  Add each user as a dict of the VM templates they can use and the quantity
### Eventually we'll read this in from some other configuration
user_config["user"]={"test":1,"kali":0}
config["dhcp_config_path"]="/var/www/dhcp.conf" ## Where to write per host reservations
config["dhcp_start"]="192.168.1.235" ## First availabe IP address for hosts, inclusive
config["dhcp_end"]="192.168.1.240" ## Last availabel IP address for hosts, inclusiv
config["dhcp_server"]="user@host" ## If a remote BIND DHCP server, the host as ssh_user@hostname
config["dhcp_restart_cmd"]="sudo service dhcp restart" ## The command to restart/reload DHCP, probably needs sudo in front
config["remote_dhcp"]=False  ## True or False
config["esx_host"]="192.168.1.35"
config["esx_user"]="administrator@vsphere.local"
config["esx_password"]="password"
config["esx_port"]=443
config["esx_datastore"]="datastore1"
config["esx_datacenter"]="Datacenter"
config["exclude_vms"]=("_") ## Any VM with this in the name will be excluded from all interaction by this script.


try:
    logging.basicConfig(level=logging.DEBUG,filename=logfile)
except:
    print("Cannot write logs. Refusing to run.")
    exit()

timestamp = str(datetime.datetime.now())



def request_id(form):
    ## This function generates a unique ID to track a request
    if "o_id" in form:
        o_id=form('o_id')
    else:
        o_id = uuid.uuid4()
    return str(o_id)

def get_environ_info():
    ### This function tries to get the relevant info from the OS we need. Because each web server and OS supplies the information differently, this function works through the possible variations.
    ## Surely there has to be a portable way to do this. 
    if 'SCRIPT_NAME' in os.environ.keys():
        path_info = os.environ['SCRIPT_NAME']
    elif 'PATH_INFO' in os.environ.keys():
        path_info = os.environ['PATH_INFO']
    else:
        path_info = ""
    if 'SERVER_NAME' in os.environ.keys():
        server_name = os.environ['SERVER_NAME']
    else:
        server_name = ""
    if 'REMOTE_USER' in os.environ.keys():
        auth_user = os.environ['REMOTE_USER']
    elif 'AUTH_USER' in os.environ.keys():
        auth_user = os.environ['AUTH_USER']
    else:
        auth_user = "unknown_user"
    if 'QUERY_STRING' in os.environ.keys():
        query_string = os.environ['QUERY_STRING']
    else:
        query_string = ""
    if 'REMOTE_ADDR' in os.environ.keys():
        remote_addr = os.environ['REMOTE_ADDR']
    else:
        remote_addr = "unknown_host"
    my_url = "http://" +server_name + path_info
    my_urn = "http://" +server_name + path_info + "?" + query_string
    return(my_url,my_urn,auth_user,remote_addr)


def connect_esx(logging):
    global config
    context = None
    if hasattr(ssl, '_create_unverified_context'):
        context = ssl._create_unverified_context()
    si = SmartConnect(host=config["esx_host"], user=config["esx_user"], pwd=config["esx_password"], port=int(config["esx_port"]), sslContext=context)
    if not si:
       print("Could not connect to the esx host")
       logging.warn(log_prefix + "Could not connect to ESX host "+esx_host+ " as user "+esx_user)
       return -1

    atexit.register(Disconnect, si)
    return si

def get_all_objs(content, vimtype):
        obj = {}
        container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
        for managed_object_ref in container.view:
                obj.update({managed_object_ref: managed_object_ref.name})
        return obj

def get_vm_list(user):
    global config
    provisioned=list()
    global user_config
    context = None
    if hasattr(ssl, '_create_unverified_context'):
        context = ssl._create_unverified_context()
    si = SmartConnect(host=config["esx_host"], user=config["esx_user"], pwd=config["esx_password"], port=int(config["esx_port"]), sslContext=context)
    if not si:
       print("Could not connect to the esx host")
       logging.warn(log_prefix + "Could not connect to ESX host "+esx_host+ " as user "+esx_user)
       return -1

    atexit.register(Disconnect, si)

    content = si.RetrieveContent()
    for child in content.rootFolder.childEntity:
      if hasattr(child, 'vmFolder'):
        datacenter = child
        vmFolder = datacenter.vmFolder
        vmList = vmFolder.childEntity
        #vmList=get_all_objs(content, [vim.VirtualMachine])
        if user in user_config["admins"]:
            print("<b>!!! ADMIN VIEW !!!</b> You can see everyone's systems. Be careful!<table>")
        else:
            print("<b>Your Provisioned Virtual Machines</b><table>")
        for vm in vmList:
            summary = vm.summary
            if ( (user in str(summary.config.name)) or (user in user_config["admins"])) and config["exclude_vms"] not in summary.config.name:
                if summary.runtime.powerState == "poweredOff":
                    powerstate = "<img src=/images/power_red.svg>Off"
                elif summary.runtime.powerState == "poweredOn":
                    powerstate = "<img src=/images/power_green.svg>On"
                else:
                    powerstate = summary.runtime.powerState
                print("<form action='"+my_url+"' method='get'><input type='hidden' name='host' value='"+summary.config.name+"'><tr>")
                print("<td>"+ summary.config.name + "</td><td>" +powerstate +"</td>")
                print("<td><button type='submit' name='action' value='reset'>Reset</button></td>")
                print("<td><button type='submit' name='action' value='poweroff'>PowerOff</button></td>")
                print("<td><button type='submit' name='action' value='poweron'>Power On</button></td>")
                print("<td><button type='submit' name='action' value='delete'>Delete</button></td>")
                print("<td><button type='submit' name='action' value='redeploy'>Wipe & Redploy</button></td>")
                print("<td><a href="+my_url+"?action=vnc_link&host="+summary.config.name+">VNC</a></td>")
                print("<td><a href="+my_url+"?action=rdp_link&host="+summary.config.name+">RDP</a></td>")
                print("</tr></form>")
                provisioned.append(str(summary.config.name))
        print("</table>")
    return(provisioned)

def make_rdp_link(host):
    print("Content-type: application/octect-stream; name = \""+host+".rdp\"")
    print("Content-disposition: attachment; filename = \""+host+".rdp\"\r\n")
    print(""" screen mode id:i:2
desktopwidth:i:1600
desktopheight:i:900
session bpp:i:32
connection type:i:7
networkautodetect:i:1
authentication level:i:2
prompt for credentials:i:0
negotiate securirt layer:i:1
username:s:user
""")
    print("full address:s:"+host)

def make_vnc_link(host):
    print("Content-type: application/octect-stream; name = \""+host+".vnc\"")
    print("Content-disposition: attachment; filename = \""+host+".vnc\"\r\n\r\n")
    print("ConnMethod=tcp\r\nHost="+host+"\r\nRelativePtr=0\r\n")

def destroy_host(host,logging):
    global config
    si = connect_esx(logging)
    content = si.content
    objView = content.viewManager.CreateContainerView(content.rootFolder,[vim.VirtualMachine],True)
    vmList = objView.view
    for vm in vmList:
        if vm.name == host:
            #if ( (user in str(vm.name)) or (user in user_config["admins"])) and config["exclude_vms"] not in vm.name:
            vm.PowerOff()
            time.sleep(2)
            vm.Destroy_Task()
            logging.info(log_prefix + "requested deletion of "+host)
            ### Remove DHCP Reservation
            path = config["dhcp_config_path"]+"/"+host+".conf"
            if os.path.exists(path):
                os.remove(path)
                ## FIXME we need to rebuild the combined DHCP config here, or exclude it from being read when looking for used IP in the dhcp_reservation function.
                logging.debug(log_prefix + "removed DHCP reservation for deleted host "+host)



def poweron_host(host,logging):
    si = connect_esx(logging)
    content = si.content
    objView = content.viewManager.CreateContainerView(content.rootFolder,[vim.VirtualMachine],True)
    vmList = objView.view
    for vm in vmList:
        if vm.name == host:
            #if ( (user in str(vm.name)) or (user in user_config["admins"])) and config["exclude_vms"] not in vm.name:
            vm.PowerOn()
            logging.info(log_prefix + "requested poweron of "+host)


def poweroff_host(host,logging):
    si = connect_esx(logging)
    content = si.content
    objView = content.viewManager.CreateContainerView(content.rootFolder,[vim.VirtualMachine],True)
    vmList = objView.view
    for vm in vmList:
        if vm.name == host:
            #if ( (user in str(vm.name)) or (user in user_config["admins"])) and config["exclude_vms"] not in vm.name:
            vm.PowerOff()
            logging.info(log_prefix + "requested poweroff of "+host)


def reset_host(host,logging):
    si = connect_esx(logging)
    content = si.content
    objView = content.viewManager.CreateContainerView(content.rootFolder,[vim.VirtualMachine],True)
    vmList = objView.view
    for vm in vmList:
        if vm.name == host:
            #if ( (user in str(vm.name)) or (user in user_config["admins"])) and config["exclude_vms"] not in vm.name:
            vm.ResetVM_Task()
            logging.info(log_prefix + "requested reset of "+host)

def get_vm_info(host,logging):
    si = connect_esx(logging)
    content = si.content
    objView = content.viewManager.CreateContainerView(content.rootFolder,[vim.VirtualMachine],True)
    vmList = objView.view
    for vm in vmList:
        if vm.name == host:
            return(vm)

### Taken directly from PyVMOMI samples
def get_obj(content, vimtype, name):
    global logging
    obj = None
    container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
    for c in container.view:
        if c.name == name:
            obj = c
            break
    return obj


def deploy_template(template,host,logging):
    ### EXPIREMENTAL NOT FINISHED
    global config
    si = connect_esx(logging)
    content = si.RetrieveContent()
    vm_template = get_obj(content, [vim.VirtualMachine], template)
    datacenter = get_obj(content, [vim.Datacenter], config["esx_datacenter"])
    datastore = get_obj(content, [vim.Datastore], config["esx_datastore"])
    destfolder = datacenter.vmFolder
    relospec = vim.vm.RelocateSpec()
    relospec.datastore = datastore
    clonespec = vim.vm.CloneSpec()
    clonespec.location = relospec
    clonespec.powerOn = True
    clonespec.template = False
    task = vm_template.Clone(folder=destfolder, name=host, spec=clonespec)
    time.sleep(5) ## Give ESX time to create the new VM
    logging.info(log_prefix + "user "+user+" requested clone of template "+template+" to "+host)
    vm = get_vm_info(host,logging)
    ## This only works for single NIC VM's
    for device in vm.config.hardware.device:
        if hasattr(device, 'macAddress'):
            mac_address = device.macAddress
    logging.debug("DEBUG: MAc Address for "+str(host)+" is "+str(mac_address))
    create_dhcp_reservation(host,mac_address)

def create_dhcp_reservation(host,mac):
    global config
    path = config["dhcp_config_path"]+"/"+host+".conf"
    file_list = glob.glob(config["dhcp_config_path"]+"/*.conf")
    existing_dhcp_ip=[] ## A list of currently allocated IP
    ## Get the list of IP already allocated in the DHCP configs
    for single_file in file_list:
        for line in open(single_file, 'r'):
            if re.search("fixed-address", line):
                address=line.split("fixed-address ")
                used_address=address[1].strip('\n')
                logging.debug("found address: "+str(used_address))
                existing_dhcp_ip.append(used_address)
    logging.debug("currently used IP: "+str(existing_dhcp_ip))
    ## Find an IP in the subnet not already used
    for ip in netaddr.iter_iprange(config["dhcp_start"],config["dhcp_end"]):
        if ip not in existing_dhcp_ip:
            continue
    logging.debug("allocating new IP: "+str(ip))
    try:
        reservation = "host "+str(host)+" {\nhardware ethernet "+str(mac)+";\nfixed-address "+str(ip)+";\n}\n"
        logging.debug("reservation content: "+str(reservation))
        f = open(path, "w")
        f.write(reservation)
        f.close()
        file_list = glob.glob(config["dhcp_config_path"]+"/*.conf")
        ## Combine all the dhcp host files into a single file which can be included into BIND DHCP
        with open(config["dhcp_config_path"]+'/combined.conf', 'w') as outfile:
            for fname in file_list:
                with open(fname) as infile:
                    for line in infile:
                        outfile.write(line)
        outfile.close()
        logging.info(log_prefix + "user "+user+" created dhcp reservation for "+host+" with mac "+str(mac)+" and ip "+str(ip))
        ## If local DHCP, restart the service to re-read the new combined config
        if config["remote_dhcp"] == False:
            subprocess.call(["sudo","/usr/sbin/service","dhcpd","restart"],shell=True)
        ## If a remote DHCP server, copy the combined config file and restart the remotse dhcp service
        if config["remote_dhcp"] == True:
            ### Must Have SSH keys setup
            scp_path = ssh_user+"@"+ssh_server+":"+path
            subprocess.run(["scp", path, scp_path])
            subprocess.run(["ssh", config["dhcp_server"], "service dhcp restart"])
    except Exception as e:
        logging.error("ERROR in DHCP function: "+str(e))



my_url,my_urn,user,remote_addr = get_environ_info()
if not user:
    print ("Content-type: text/html\r\n\r\n")
    print ("<html><head></head><body>You must log in. Unknown User.</body></html>")
    exit()

form = cgi.FieldStorage()
o_id=request_id(form)
log_prefix = str(timestamp) + " "+ o_id + " "  + str(user) + "@" +str(remote_addr)+ " "
logging.info(log_prefix + "connected")
logging.debug(log_prefix + "received form values: " + str(form))

action = form.getvalue("action")
host = form.getvalue("host")
if (host) and (user not in host):
    #if ( config["exclude_vms"] not in host):
    print ("Content-type: text/html\r\n\r\n")
    print("I'm sorry "+user+", I can't let you do that. (It doesn't look like "+host+" is your vm.)<br><a href="+my_url+">Home</a>")
    logging.warn(log_prefix + "user "+user+" tried to take action on a VM "+host+" they don't own")
    exit()


print ("Content-type: text/html\r\n\r\n")
if action == "vnc_link":
    make_vnc_link(host)
    exit()
elif action == "rdp_link":
    make_rdp_link(host)
    exit()
elif action == "poweron":
    poweron_host(host,logging)
elif action == "poweroff":
    poweroff_host(host,logging)
elif action == "reset":
    reset_host(host,logging)
elif action == "delete":
    destroy_host(host,logging)
elif action == "deploy_template":
    template = form.getvalue("template")
    deploy_template(template,host,logging)



if action != None:
    ## This refreshes the page after an action so the user sees the change. 
    print("<meta http-equiv='refresh' content=\"5;URL='"+my_url+"'\" />")

provisioned = get_vm_list(user)
print("<b>Your Available Virtual Machine Images</b><table>")
for vm in user_config[user]:
    if vm+"-"+user not in provisioned:
        print("<form action='"+my_url+"' method='get'><input type='hidden' name='host' value='"+vm+"-"+user+"'><input type='hidden' name='template' value='"+vm+"'><tr><td>"+vm+"</td><td><button type='submit' name='action' value='deploy_template'>Deploy</button></td></tr></form>")
print("</table>")
exit()

