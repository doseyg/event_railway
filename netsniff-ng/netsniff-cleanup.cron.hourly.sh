#!/bin/sh
## Keep 1440 minutes/24 hours worth of pcap data
source /etc/sysconfig/netsniff-ng
find $DATA_DIR -type f -mmin +1440 -uid $USER -exec rm -f {} \;
