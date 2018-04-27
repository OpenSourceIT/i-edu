class usb::vendor_kingston ($status="present", $vm_names) {
	
	usbdevice { $vm_names:
		vendorid => "0951",
		status => $status,
	}
}
