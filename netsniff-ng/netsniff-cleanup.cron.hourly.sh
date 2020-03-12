#!/bin/sh
## Keep 1440 minutes/24 hours worth of pcap data
source /etc/sysconfig/netsniff-ng
find $DATA_DIR -type f -mmin +$DATA_EXPIRE -uid $USER -exec rm -f {} \;
