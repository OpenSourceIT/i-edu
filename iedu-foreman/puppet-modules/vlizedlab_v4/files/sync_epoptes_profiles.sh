#!/bin/bash

TEMPLATE_USER="iteasadm"
USERS="epoptes1 epoptes2 epoptes3 epoptes4"

for USER in $USERS;
do
	mkdir -p /home/$USER/.config/epoptes
	cp /home/$TEMPLATE_USER/.config/epoptes/* /home/$USER/.config/epoptes
	chown -R $USER:epoptes-users /home/$USER/.config
done

