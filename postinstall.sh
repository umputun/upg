#!/bin/sh

# This script sets permissions on the UPG installtion
# and install the init script.
#
# Run this script as root after installation of UPG
# It is expected that you are executing this script from the bin directory

# If you used an non standard directory name of location
# Please specify it here
# UPG_HOME=

UPG_USER="upg"
UPG_GROUP="upg"

if [ ! $UPG_HOME ]; then
        if [ -d "/opt/upg" ]; then
                UPG_HOME="/opt/upg"
        elif [ -d "/usr/local/upg" ]; then
                UPG_HOME="/usr/local/upg"
        fi
fi

# Install the init script
cp $UPG_HOME/upgd /etc/init.d
/sbin/chkconfig --add upgd
/sbin/chkconfig upgd on

# Create the upg user and group
/usr/sbin/groupadd $UPG_GROUP
/usr/sbin/useradd $UPG_USER -g $UPG_GROUP

# Change the permissions on the installtion directory
/bin/chown -R $UPG_USER:$UPG_GROUP $UPG_HOME


