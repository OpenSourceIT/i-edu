class usb::vendor_custom2 (String $status="present", Array $vm_names, String $vendorid, String $productid) {

	$vm_names.each |String $vm_name| {
		usb::usbdevice { "c2-${vm_name}":
			vendorid => $vendorid,
			productid => $productid,
			status => $status,
			vmname => $vm_name,
		}
	}
}
