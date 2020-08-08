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
print ("Content-type: text/html\r\n\r\n")

### Config variables ###
logfile='file.log'
interactive=True
enabled_actions=('kill_process') ## A list of enabled action names (without the .py extension)
modules_dir="/var/www/cgi-bin/modules/"

try:
    logging.basicConfig(level=logging.DEBUG,filename=logfile)
except:
    print("Cannot write logs. Refusing to run.")
    exit()

timestamp = str(datetime.datetime.now())



def modules_setup(logging):
    ### This function checks the contents of, updates, and ensures the __init__.py file in the modules directory will load each module in that directory
    #### FIXME IIS needs full path to modules directory, not relative path
    modules_init =  """
__all__ = []

import pkgutil
import inspect

for loader, name, is_pkg in pkgutil.walk_packages(__path__):
    module = loader.find_module(name).load_module(name)

    for name, value in inspect.getmembers(module):
        if name.startswith('__'):
            continue

        globals()[name] = value
        __all__.append(name) """
    try:
        file=open(modules_dir + "/__init__.py", "r").read()
    except: 
        file=""
        logging.info("__init__.py in modules directory could not be read")
    if file == modules_init:
       logging.debug("__init__.py in modules directory is correct")
    else:
        try:
            logging.info("__init__.py in modules directory needs updating")
            file=open( modules_dir + "/__init__.py", "w")
            file.write(modules_init)
            file.close()
            logging.info("__init__.py in modules directory successfully updated")
        except:
            print ("__init__.py file in modules directory missing or changed and cannot write to update it")
            logging.critical("__init__.py file in modules directory missing or changed and cannot write to update it")
            exit()


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

my_url,user,remote_addr = get_environ_info()
form = cgi.FieldStorage()
o_id=request_id(form)
log_prefix = str(timestamp) + " "+ o_id + " "  + str(user) + "@" +str(remote_addr)+ " "
logging.info(log_prefix + "connection")


modules_setup(logging)
#from modules import *


logging.debug(log_prefix + "received form values: " + str(form))

if "action" not in form:
    print ("<html><head></head><body>This is an odd place.</body></html>")
    exit()
else:
    action = form.getvalue('action')


if interactive==True:
    if form.getvalue("confirm") == "True":
        print("Confirmed<br>")
    else:
        print("Please confirm you your action:<br>")
        print("<table>")
        for key in form.keys():
                print("<tr><td>" + str(key)+" </td><td> "+ str(form.getvalue(key)) + "</td></tr>")
        print("</table>")
        print("<a href="+my_url+"&confirm=True>Confirm</a>")
        exit()

if action in enabled_actions:
    import importlib
    sys.path.append(modules_dir)
    print("Executing action: " + str(action))
    action_module = __import__(action,fromlist=['*'])
    print(sys.modules[action].action_class.required_vars())
    sys.modules[action].action_class.do_action(form,logging)
else: 
    print("Unknown Action: "+ str(action))
    logging.error(log_prefix + "undefined action: " + str(action))
    exit()



