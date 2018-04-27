class vm::vm_settings ($status="present", $vm_names, $vm_settings) {
	
	vm::setting { $vm_names:
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
