#!/bin/bash

if [ -f "/usr/local/etc/dom_joined" ]; then
	echo "Dieser Computer wurde schon gejoined. Bitte /usr/local/etc/dom_joined entfernen und erneut versuchen."
	exit 1
fi

#HOST_UUID=$(cat /dev/urandom | tr -dc 'a-z0-9' | fold -w 7 | head -n 1)
until s=$(dd bs=21 count=1 if=/dev/urandom | tr -dc 'a-z0-9')
	((${#s} >= 10)); do :; done
HOST_UUID=${s:0:7}
HOST_NAME="kubuntu-$HOST_UUID"

echo "Neuer Hostname:$HOST_NAME"

hostnamectl set-hostname $HOST_NAME
sed -i "s/127.0.1.1\\tkubuntu-[a-z0-9]*/127.0.1.1\\t$HOST_NAME/" /etc/hosts

systemctl restart systemd-logind.service

echo "; ; ; ; ; ; ; ; ; ;" | net ads join -U user%password

echo "yes" > /usr/local/etc/dom_joined

shutdown -h now

#sleep 11
#systemctl start lxdm.service
