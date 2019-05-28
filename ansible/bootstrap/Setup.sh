#!/bin/sh
## For Ansible bootstrap on CentOS 7 minimal install
## To download offline packages: pip download -d python-deps pyvmomi pysphere pywinrm
## To install offline packages: pip install --no-index --find-links pthons-deps/ pyvmomi pysphere pywinrm

yum -y install epel-release
yum -y install ansible python2-pip


ansible-playbook bootstrap.yml
exit;

pip install pyvmomi
pip install pysphere
pip install pywinrm



## Configure PXE boot server
yum install tftp-server tftp dhcp syslinux vsftpd
cp /usr/share/doc/dhcp-*/dhcpd.conf.example /etc/dhcp/dhcpd.conf

sed -i 's/.*disable.*=.*yes.*/\tdisable = no/' /etc/xinetd.d/tftp
cp -v /usr/share/syslinux/pxelinux.0 /var/lib/tftpboot
cp -v /usr/share/syslinux/menu.c32 /var/lib/tftpboot
cp -v /usr/share/syslinux/memdisk /var/lib/tftpboot
cp -v /usr/share/syslinux/mboot.c32 /var/lib/tftpboot
cp -v /usr/share/syslinux/chain.c32 /var/lib/tftpboot

mount -o loop CentOS-7-x86_64-DVD-1511.iso /mnt/
cp -av /mnt/* /var/ftp/pub/

yum install httpd
