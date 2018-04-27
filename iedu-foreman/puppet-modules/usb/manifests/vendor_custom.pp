class usb::vendor_custom (String $status="present", Array $vm_names, String $vendorid, String $productid) {

	$vm_names.each |String $vm_name| {
		usb::usbdevice { "c-${vm_name}":
			vendorid => $vendorid,
			productid => $productid,
			status => $status,
			vmname => $vm_name,
		}
	}
}
