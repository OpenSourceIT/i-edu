class vlizedlab_v4::app_smc (String $status = "present", String $res = '1280x1024') {

	package { ['smc', 'smc-data', 'smc-music']:
      ensure => latest,
    }

    file { "/etc/vlizedlab/startmenu.d/smc":
      ensure => $status,
      source => "puppet:///modules/vlizedlab_v4/startmenustudentgui.static.smc",
      require => [Package['smc'], File["/etc/vlizedlab/startmenu.d"]]
    }

	file { "/usr/share/icons/smc_logo.png":
      ensure => present,
      mode => '644',
      source => "puppet:///modules/vlizedlab_v4/smc_logo.png",
    }

	#file { "/home/student/.config/supertuxkart":
    #  ensure => directory,
    #  owner => "student",
    #  group => "student",
    #  require => Package['iedu-client'],
    #}

    #file { "/home/student/.config/supertuxkart/config.xml":
    #  ensure => present,
    #  source => "puppet:///modules/vlizedlab_v4/config_supertuxkart_$res.xml",
    #  owner => "student",
    #  group => "student",
    #  require => [Package['smc']]
    #}

}
