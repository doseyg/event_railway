#!/usr/bin/python3
###  doseyg@r-networks.net 
###  May 2019
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
print ("Content-type: text/html\r\n\r\n")

### Config variables ###
logfile='vm_manager.log'
interactive=False
enabled_actions=('kill_process') ## A list of enabled action names (without the .py extension)

user_config={}
### Add any admin user names here. 
user_config["admins"]=("admin","bob")
###  Add each user as a dict of the VM templates they can use and the quantity
user_config["user"]={"test":1,"kali":0}


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
    my_url = "http://" +server_name + path_info + "?" + query_string
    return(my_url,auth_user,remote_addr)


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
       print("Could not connect to the esx host using")
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
                print("<form action='/vm.py' method='get'><input type='hidden' name='host' value='"+summary.config.name+"'><tr><td>"+ summary.config.name + "</td><td>" +summary.runtime.powerState +"</td><td><button type='submit' name='action' value='reset'>Reset</button></td><td><button type='submit' name='action' value='poweroff'>PowerOff</button></td><td><button type='submit' name='action' value='poweron'>Power On</button></td><td><button type='submit' name='action' value='redeploy'>Wipe & Redploy</button></td></tr></form>")
                provisioned.append(str(summary.config.name))
        print("</table>")
    return(provisioned)



my_url,user,remote_addr = get_environ_info()
form = cgi.FieldStorage()
o_id=request_id(form)
log_prefix = str(timestamp) + " "+ o_id + " "  + str(user) + "@" +str(remote_addr)+ " "
logging.info(log_prefix + "connection")



logging.debug(log_prefix + "received form values: " + str(form))

if not user:
    print ("<html><head></head><body>You must log in. Unknown User.</body></html>")
    exit()


provisioned = get_vm_list(user)
print("<b>Your Available Virtual Machine Images</b><table>")
for vm in user_config[user]:
    if vm+"-"+user not in provisioned:
        print("<form action='/vm.py' method='get'><input type='hidden' name='host' value='"+vm+"'><tr><td>"+vm+"</td><td><button type='submit' name='action' value='deploy'>Deploy</button></td></tr>")
print("</table>")
exit()

