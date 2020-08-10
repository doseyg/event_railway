#!/usr/bin/python3
###  doseyg@r-networks.net 
###  May 2020
import os
import cgi, cgitb
import datetime ## For timestamps in logging
import logging ## Implements logging
import getpass ## Used to get username 
import uuid
import sys
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
import ssl
import atexit
import time ## for sleep delay

### Config variables ###
logfile='vm_manager.log'

user_config={}
### Add any admin user names here. 
user_config["admins"]=("admin","bob")
user_config["unknown_user"]={}
###  Add each user as a dict of the VM templates they can use and the quantity
### Eventually we'll read this in from some other configuration
user_config["user"]={"test":1,"kali":0}


try:
    logging.basicConfig(level=logging.INFO,filename=logfile)
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
    esx_host="192.168.1.176"
    esx_user="root"
    esx_password="password"
    esx_port=443
    context = None
    if hasattr(ssl, '_create_unverified_context'):
        context = ssl._create_unverified_context()
    si = SmartConnect(host=esx_host, user=esx_user, pwd=esx_password, port=int(esx_port), sslContext=context)
    if not si:
       print("Could not connect to the esx host")
       logging.warn(log_prefix + "Could not connect to ESX host "+esx_host+ " as user "+esx_user)
       return -1

    atexit.register(Disconnect, si)
    return si



def get_vm_list(user):
    esx_host="192.168.1.176"
    esx_user="root"
    esx_password="password"
    esx_port=443
    provisioned=list()
    context = None
    if hasattr(ssl, '_create_unverified_context'):
        context = ssl._create_unverified_context()
    si = SmartConnect(host=esx_host, user=esx_user, pwd=esx_password, port=int(esx_port), sslContext=context)
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

        print("<b>Your Provisioned Virtual Machines</b><table>")
        for vm in vmList:
            summary = vm.summary
            if user in str(summary.config.name):
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
    si = connect_esx(logging)
    content = si.content
    objView = content.viewManager.CreateContainerView(content.rootFolder,[vim.VirtualMachine],True)
    vmList = objView.view
    for vm in vmList:
        if vm.name == host:
            vm.PowerOff()
            time.sleep(2)
            vm.Destroy_Task()
            logging.info(log_prefix + "requested deletion of "+host)



def poweron_host(host,logging):
    si = connect_esx(logging)
    content = si.content
    objView = content.viewManager.CreateContainerView(content.rootFolder,[vim.VirtualMachine],True)
    vmList = objView.view
    for vm in vmList:
        if vm.name == host:
            vm.PowerOn()
            logging.info(log_prefix + "requested poweron of "+host)


def poweroff_host(host,logging):
    si = connect_esx(logging)
    content = si.content
    objView = content.viewManager.CreateContainerView(content.rootFolder,[vim.VirtualMachine],True)
    vmList = objView.view
    for vm in vmList:
        if vm.name == host:
            vm.PowerOff()
            logging.info(log_prefix + "requested poweroff of "+host)


def reset_host(host,logging):
    si = connect_esx(logging)
    content = si.content
    objView = content.viewManager.CreateContainerView(content.rootFolder,[vim.VirtualMachine],True)
    vmList = objView.view
    for vm in vmList:
        if vm.name == host:
            vm.ResetVM_Task()
            logging.info(log_prefix + "requested reset of "+host)

def deploy_template(template,host):
    print(" ")



my_url,my_urn,user,remote_addr = get_environ_info()
if not user:
    print ("Content-type: text/html\r\n\r\n")
    print ("<html><head></head><body>You must log in. Unknown User.</body></html>")
    exit()

form = cgi.FieldStorage()
o_id=request_id(form)
log_prefix = str(timestamp) + " "+ o_id + " "  + str(user) + "@" +str(remote_addr)+ " "
logging.info(log_prefix + "connection")
logging.debug(log_prefix + "received form values: " + str(form))

action = form.getvalue("action")
host = form.getvalue("host")
if (host) and (user not in host):
    print ("Content-type: text/html\r\n\r\n")
    print("I'm sorry "+user+", I can't let you do that. (It doesn't look like "+host+" is your vm.)<br><a href="+my_url+">Home</a>")
    logging.warn(log_prefix + "user "+user+" tried to take action on a VM "+host+" they don't own")
    exit()


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



print ("Content-type: text/html\r\n\r\n")
if action != None:
    ## This refreshes the page after an action so the user sees the change. 
    print("<meta http-equiv='refresh' content=\"5;URL='"+my_url+"'\" />")

provisioned = get_vm_list(user)
print("<b>Your Available Virtual Machine Images</b><table>")
for vm in user_config[user]:
    if vm+"-"+user not in provisioned:
        print("<form action='/vm.py' method='get'><input type='hidden' name='host' value='"+vm+"'><tr><td>"+vm+"</td><td><button type='submit' name='action' value='deploy'>Deploy</button></td></tr></form>")
print("</table>")
exit()

