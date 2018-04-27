define usb::usbdevice (String $vendorid, String $productid="", String $status="present", String $vmname)
{
	file { "/etc/vlizedlab/vm_usb_filter.d/usb-$vendorid$productid-$name":
      ensure => $status,
      content => "$vmname,$vendorid,$productid",
      require => Package['iedu-client'],
    }
}
