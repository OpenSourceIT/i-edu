class vlizedlab_v4::wlan_aus_lan_ein {

    file { "/etc/network/interfaces":
      ensure => present,
      mode => '644',
      source => "puppet:///modules/vlizedlab_v4/interfaces_fuer_lan",
    }

    exec { "cmd-reboot-after-config":
        command => "reboot",
        path    => "/usr/bin/:/usr/sbin/:/bin/:sbin",
        refreshonly => true,
		subscribe => File["/etc/network/interfaces"],
    }

	file { "/home/student/.i3status.conf":
      ensure => present,
      owner => "student",
      group => "student",
      mode => '644',
      source => "puppet:///modules/vlizedlab_v4/i3status_lan",
    }
}

