#!/bin/bash

# doesnt make sense for setup outside the chmod of the upcoming system
#if [ ! -f /etc/apt/apt.conf.d/02proxy ]; then
#   if ( echo '' | telnet aptcache 3142 2> /dev/null | grep -q 'Connected to' ); then
#       # echo "Found apt-cacher at aptcache; setting proxy"
#       echo 'Acquire::http::Proxy "http://aptcache:3142";' > /etc/apt/apt.conf.d/02proxy
#   elif ( echo '' | telnet vlizedlabroot 3142 2> /dev/null | grep -q 'Connected to' ); then
#       # echo "Found apt-cacher at vlizedlabroot; setting proxy"
#       echo 'Acquire::http::Proxy "http://vlizedlabroot:3142";' > /etc/apt/apt.conf.d/02proxy
#   else
#       # echo "No apt-cacher found"
#       echo '// Acquire::http::Proxy "http://aptcache:3142";' > /etc/apt/apt.conf.d/02proxy
#   fi
#fi
