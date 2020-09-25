## Web page to provide simple management interface for user's to manage their own running user VM's
Just a front-end to some ESX API calls. User's can clone their own copy of configured VM templates, and then start, stop, delete and re-deploy it. 
![Screenshot](/doseyg/eent_railway/vm_manager/screenshot.png)
### Setup
#### ESX Connection
Complete the variables esx_host(ip), esx_user, esx_port(443), and esx_password at the top of the script.
#### DHCP
We use DHCP for the VMs, so make the directory /etc/dhcp/conf.d on the server running the webpage. We'll write configs here and then merge them, optionally copying to a different DHCP server. 
#### User Permissions
User's can only see their own VMs. VMs are named in the scheme of VMname-userName. You define what template a user can clone in the dict user_config["user_name"]={"template_name":qty,"template2":1} Currently aloowing multiple copies of a VM isn't implemented, but planned for.
#### Admins
You can define admins who can see everyone's vm in the variable user_config["admins"]=("userA","userB") etc... It's just a python list, so make sure it is enclose in the parens. 




