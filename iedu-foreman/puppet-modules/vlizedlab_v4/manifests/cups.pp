class vlizedlab_v4::cups {

    package { 'cups':
      ensure => installed,
    }

    package { 'avahi-daemon':
      ensure => installed,
    }

	package { 'avahi-utils':
      ensure => installed,
    }

	file { "/etc/nsswitch.conf":
      ensure => present,
      mode => '0644',
      source => "puppet:///modules/vlizedlab_v4/nsswitch.conf",
      require => Package['avahi-daemon'],
    }

}
