class vlizedlab_v4::wlan_ein_lan_aus {

    package { 'wpasupplicant':
      ensure => installed,
    }

    package { 'wireless-tools':
      ensure => installed,
    }

    file { "/etc/wpa_supplicant/wpa_supplicant.conf":
      ensure => present,
      mode => '600',
      source => "puppet:///modules/vlizedlab_v4/wpa_supplicant.conf",
      require => [Package['wpasupplicant'], Package['wireless-tools']]
    }

    file { "/etc/network/interfaces":
      ensure => present,
      mode => '644',
      source => "puppet:///modules/vlizedlab_v4/interfaces_fuer_wlan",
	  require => [Package['wpasupplicant'], Package['wireless-tools'], File['/etc/wpa_supplicant/wpa_supplicant.conf']]
    }

	file { "/home/student/.i3status.conf":
      ensure => present,
	  owner => "student",
	  group => "student",
      mode => '644',
      source => "puppet:///modules/vlizedlab_v4/i3status_wlan",
    }

    exec { "cmd-reboot-after-config":
        command => "reboot",
        path    => "/usr/bin/:/usr/sbin/:/bin/:/sbin",
        refreshonly => true,
		subscribe => File["/etc/network/interfaces"],
    }


}

