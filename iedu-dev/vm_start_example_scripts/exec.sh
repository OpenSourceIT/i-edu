#!/bin/bash -x

#
# (c) Rene Hadler, iteas IT Services GmbH
# rene.hadler@iteas.at
# www.iteas.at
#

VMDIR="/vm/vb/$MACHINE"

export INITVM=1

_clean () {
     VBoxManage --nologo unregistervm $MACHINE

     if [ -f $MACHINEDIR/$MACHINE.xml ]; then
         rm $MACHINEDIR/$MACHINE.xml
     fi

     if [ -f $MACHINEDIR/$MACHINE.vbox ]; then
         rm $MACHINEDIR/$MACHINE.vbox
     fi

     if [ -d $MACHINEDIR/$MACHINE ]; then
         rm -Rf $MACHINEDIR/$MACHINE
     fi
}

echo "$MACHINEDIR##$MACHINE" > /tmp/startvmvar

VP="`ps augx | grep VirtualBox | grep $MACHINE | grep -v grep | head -1 | awk '{print $2}'`"

if [ ! -z "$VP" ]; then # Vbox machine ist still running. Kill it.

    echo "killing orphaned VirtualBox machine $VP..."
    kill $VP
    sleep 1
    if ps --pid $VP > /dev/null; then sleep 3; fi
    if ps --pid $VP > /dev/null; then kill -9 $VP; fi

fi

VBoxManage --nologo unregistervm $MACHINE

echo "Examining Configuration for System"

CCPU=`cat /proc/cpuinfo | grep -i vendor_id | wc -l`
CMEM=`grep MemTotal /proc/meminfo | awk '{print $2}'`
VGAPCIID=`lspci | grep VGA | awk '{print $1}'`
CVMEM=`lspci -v -s $VGAPCIID | grep " prefetchable" | cut -f2 -d= | cut -f1 -dM`

VBOX_CPU=$CCPU
VBOX_RAM=$(($CMEM / 1024 / 100 * 60))
VBOX_VRAM=$CVMEM

if [ $VBOX_RAM -gt 4096 ]; then
    VBOX_RAM=4096
fi

if [ $VBOX_VRAM -gt 256 ]; then
    VBOX_VRAM=256
fi

if [ $VBOX_CPU -gt 4 ]; then
    VBOX_CPU=4
fi

sed -i "s/--memory [0-9]*/--memory $VBOX_RAM/" "$VMDIR/init.sh"
sed -i "s/--vram [0-9]*/--vram $VBOX_VRAM/" "$VMDIR/init.sh"
sed -i "s/--cpus [0-9]*/--cpus $VBOX_CPU/" "$VMDIR/init.sh"

echo "Starting Virtual Machine vb/$MACHINE"

$VMDIR/init.sh >>/tmp/vlstartvbmachine.log 2>&1

VBoxManage --nologo startvm $MACHINE >>/tmp/vlstartvbmachine.log 2>&1

# Warte fuer Domainjoin und beende VM
sleep 30

VBoxManage controlvm $MACHINE acpipowerbutton

echo "ok delete exec" >> /tmp/startvmvar

_clean

rm -f "$VMDIR/exec.sh"
