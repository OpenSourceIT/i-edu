class vlizedlab_v4::app_kodi ($status = "present") {

    file { "/etc/apt/sources.list.d/team-xbmc-ubuntu-ppa-xenial.list":
      ensure => $status,
      source => "puppet:///modules/vlizedlab_v4/team-xbmc-ubuntu-ppa-xenial.list",
      notify => Exec['cmd-update-xbmc-ppa'],
    }

    exec { "cmd-update-xbmc-ppa":
        command => "apt-key adv --recv-keys --keyserver keyserver.ubuntu.com 91E7EE5E && apt update",
        path    => "/usr/bin/:/usr/sbin/:/bin/",
        refreshonly => true,
    }

    package { ['kodi', 'cifs-utils']:
      ensure => installed,
      require => [ File['/etc/apt/sources.list.d/team-xbmc-ubuntu-ppa-xenial.list'] ],
    }

	package { ["kodi-audioencoder-lame"]:
		ensure => installed
	}

	package { ["libdvdcss2", "libavcodec-extra", "gstreamer1.0-fluendo-mp3", "gstreamer1.0-plugins-bad", "gstreamer1.0-plugins-bad-faad", "gstreamer1.0-plugins-ugly", "gstreamer1.0-plugins-ugly-amr", "oxideqt-codecs-extra", "libav-tools"]:
		ensure => installed
    }

    file { "/etc/vlizedlab/startmenu.d/kodi":
      ensure => $status,
      source => "puppet:///modules/vlizedlab_v4/startmenustudentgui.static.kodi",
      require => [Package['kodi'], File["/etc/vlizedlab/startmenu.d"]]
    }

}
