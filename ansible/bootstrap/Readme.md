This playbook is intended to run interactively, it will prompt you to insert the CentOS 7 and ESXi installer CDs. 

This role will configure a CentOS 7 host as a DHCP, TFTP, PXE and HTTP server.
It will configure the necessary directory structure to boot ESXi and CentOS hosts via PXE. 
Playbooks to perform unattended installs of ESXi using iDRAC and CentOS7 are included. 

To start, type 'sh Setup.sh'
If the system is not online, you will need to the CentOS Full DVD inserted and the CentOS-Media repository enabled 
