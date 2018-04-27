class vlizedlab_v4::app_makemkv ($status = "present") {

	file { "/etc/apt/sources.list.d/heyarje-ubuntu-makemkv-beta-xenial.list":
      ensure => $status,
      source => "puppet:///modules/vlizedlab_v4/heyarje-ubuntu-makemkv-beta-xenial.list",
      notify => Exec['cmd-update-makemkv-ppa'],
    }

	exec { "cmd-update-makemkv-ppa":
        command => "apt-key adv --recv-keys --keyserver keyserver.ubuntu.com 94B56C64CA7278ECFC34E8808540356019F7E55B && apt update",
        path    => "/usr/bin/:/usr/sbin/:/bin/",
        refreshonly => true,
    }

    package { "makemkv-bin":
      ensure => installed,
      require => [ File['/etc/apt/sources.list.d/heyarje-ubuntu-makemkv-beta-xenial.list'] ],
    }

    file { "/etc/vlizedlab/startmenu.d/makemkv":
      ensure => $status,
      source => "puppet:///modules/vlizedlab_v4/startmenustudentgui.static.makemkv",
      require => [Package['makemkv-bin'], File["/etc/vlizedlab/startmenu.d"]]
    }

}
