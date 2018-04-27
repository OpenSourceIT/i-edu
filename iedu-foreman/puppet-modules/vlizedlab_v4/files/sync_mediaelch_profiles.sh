#!/bin/bash

TEMPLATE_USER="iteasadm"
USERS="mediaelch1 mediaelch2 mediaelch3 mediaelch4"

for USER in $USERS;
do
	mkdir -p /home/$USER/.config/kvibes/
	cp /home/$TEMPLATE_USER/.config/kvibes/MediaElch.conf /home/$USER/.config/kvibes/
	chown -R $USER:mediaelch-users /home/$USER/.config
done

