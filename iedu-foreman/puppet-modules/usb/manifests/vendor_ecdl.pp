class usb::vendor_ecdl (String $status="present", $vm_names) {
	
	usb::usbdevice { $vm_names:
		vendorid => "090c",
		productid => "1000",
		status => $status,
	}
}
