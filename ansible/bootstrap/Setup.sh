#!/bin/sh
## For Ansible bootstrap on CentOS 7 minimal install
## To download offline packages: pip download -d python-deps pyvmomi pysphere pywinrm
## To install offline packages: pip install --no-index --find-links pthons-deps/ pyvmomi pysphere pywinrm

yum -y install epel-release
yum -y install ansible python2-pip


ansible-playbook bootstrap.yml
exit;
