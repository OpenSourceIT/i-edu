#!/bin/sh

#if [ "`debconf-get-selections | grep xserver-xorg/config/inputdevice/keyboard/layout | awk '{print $4}'`" = "de" ]; then
##     echo "Setting German Keyboard"
#    setxkbmap -layout de
#else
#    setxkbmap -layout us
#fi

## exec ion3 &

#RESFILE=$HOME/vlXresolution
## export DISPLAY=:0.0

#if [ -f $RESFILE ]; then
#   RESOLUTION="`cat $RESFILE | egrep -v '^#' | egrep '^[ \t]*[0-9][0-9]*x[0-9][0-9]' | head -1`"
#	# todo: also watch end of line in $RESFILE
#   if [ "$RESOLUTION" != "" ]; then
#      echo "Setting initial X resolution to $RESOLUTION" | logger
#      xrandr -s $RESOLUTION 2>&1 | logger
#   fi
#fi

#exec ck-launch-session i3 &

#( sleep 4 && ( devmon --no-gui --sync --mount-options "noexec,nosuid,noatime,uid=1000,gid=1000,umask=002" 2>&1 | logger -t devmon ) ) &

#exec x11vnc -nocursorshape \
#       -xwarppointer \
#       -nodragging \
#       -noxdamage \
#       -forever \
#       -shared -forever -listen 127.0.0.1  \
#	  -display :0 &

##        -rfbauth /usr/share/vlizedlad/data/passwd  \

#exec /usr/sbin/epoptes-client &

##exec xterm -fn 9x15bold -title "Virtual Machine Start Menu" -e /usr/share/vlizedlab/scripts/startmenustudent
#exec /usr/share/vlizedlab/scripts/startmenustudentgui.py



