class vm::vm3_setting (String $status="present", String $vm_name, String $network, String $macaddr, String $bridgeadapter, String $usbmode, Boolean $accelerate2dvideo, Boolean $accelerate3d, String $monitorcount, Boolean $readonly) {
	
	if($accelerate2dvideo == true) {
		$set_accelerate2dvideo = "on"
	} else {
		$set_accelerate2dvideo = ""
	}

	if($accelerate3d == true) {
        $set_accelerate3d = "on"
    } else {
        $set_accelerate3d = ""
    }

	$vm_settings = {
	  $vm_name => {	
		"network" => $network,
		"macaddr" => $macaddr,
		"bridgeadapter" => $bridgeadapter,
		"usbmode" => $usbmode,
		"accelerate2dvideo" => $set_accelerate2dvideo,
		"accelerate3d" => $set_accelerate3d,
		"monitorcount" => $monitorcount,
		"readonly" => $readonly
	  }
	}

	vm::setting { $vm_name:
		config => $vm_settings,
		status => $status,
	}

	$vm_base = "/vm/vb"

	$vm_settings.each |String $vm, Hash $setting| {

	  if ($setting["readonly"] == false) {
		$readonly = false
	  } else {
		$readonly = true
	  }

	  if ($readonly == true) {
		exec { "update-vm-config-${vm}":
            command => "sed -i 's/^INITVM=1/#INITVM=1/' ${vm_base}/${vm}/init.sh",
            path    => "/usr/bin/:/usr/sbin/:/bin/",
            onlyif  => ["test -f ${vm_base}/${vm}/init.sh", "grep '^INITVM=1' ${vm_base}/${vm}/init.sh"],
        }
	  } else {
	  	exec { "update-vm-config-${vm}":
        	command => "sed -i 's/^#INITVM=1/INITVM=1/' ${vm_base}/${vm}/init.sh",
        	path    => "/usr/bin/:/usr/sbin/:/bin/",
        	onlyif  => ["test -f ${vm_base}/${vm}/init.sh", "grep '^#INITVM=1' ${vm_base}/${vm}/init.sh"],
      	}
	  }	  
    }
}
