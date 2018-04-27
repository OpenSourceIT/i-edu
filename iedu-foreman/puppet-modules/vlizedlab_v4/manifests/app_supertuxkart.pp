class vlizedlab_v4::app_supertuxkart ($status = "present", $res = '1280x1024') {

	package { 'supertuxkart':
      ensure => latest,
    }

    file { "/etc/vlizedlab/startmenu.d/supertuxkart":
      ensure => $status,
      source => "puppet:///modules/vlizedlab_v4/startmenustudentgui.static.supertux",
      require => [Package['supertuxkart'], File["/etc/vlizedlab/startmenu.d"]]
    }

	file { "/home/student/.config/supertuxkart":
      ensure => directory,
      owner => "student",
      group => "student",
      require => Package['iedu-client'],
    }

    file { "/home/student/.config/supertuxkart/config.xml":
      ensure => present,
      source => "puppet:///modules/vlizedlab_v4/config_supertuxkart_$res.xml",
      owner => "student",
      group => "student",
      require => [Package['supertuxkart']]
    }

}
