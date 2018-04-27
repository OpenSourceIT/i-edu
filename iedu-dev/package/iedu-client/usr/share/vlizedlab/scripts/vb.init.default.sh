#!/bin/bash -x

VERSION=2

echo "starting MACHINE >$MACHINE< in >$MACHINEDIR<"

VBoxManage --nologo createvm --name $MACHINE --register --basefolder $MACHINEDIR

# VBoxManage --nologo modifyvm $MACHINE 	--ostype linux26
VBoxManage --nologo modifyvm $MACHINE \
        --memory 750 \
 	--vram 128 \
 	--acpi on \
 	--ioapic on \
 	--hwvirtex on \
 	--bioslogofadein off \
 	--bioslogofadeout off \
 	--bioslogodisplaytime 1 \
 	--nic1 nat \
 	--audio alsa \
 	--accelerate2dvideo on

# Turn this off by default:
# VBoxManage --nologo modifyvm $MACHINE 	--accelerate3d on

#Start Virtal Machine in Fullscreen
VBoxManage --nologo setextradata $MACHINE GUI/Fullscreen on

#Hide Manubar and Statusbar
VBoxManage --nologo setextradata $MACHINE GUI/Customizations noMenuBar,noStatusBar
# VBoxManage --nologo setextradata $MACHINE GUI/Customizations noStatusBar

#Hide MiniToolBar
VBoxManage --nologo setextradata $MACHINE GUI/ShowMiniToolBar no

#Set Alignment of MiniToolaBar
#VBoxManage --nologo setextradata $MACHINE GUI/MiniToolBarAlignment bottom

#Only allow Powerdown on "HOSTKEY+Q"
VBoxManage --nologo setextradata $MACHINE GUI/RestrictedCloseActions SaveState,Shutdown,Restore

if [ -f $MACHINEDIR/init.add.sh ]; then
    source $MACHINEDIR/init.add.sh
fi

VBoxManage --nologo sharedfolder add $MACHINE  --name media --hostpath /media --automount

VBoxManage --nologo storagectl    $MACHINE --name C$MACHINE --add ide --controller PIIX4 --hostiocache on
VBoxManage --nologo storageattach $MACHINE --storagectl C$MACHINE --port 1 --device 0 \
      --type hdd --medium $MACHINEDIR/$MACHINE.vdi --mtype immutable


