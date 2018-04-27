class vlizedlab_v4::app_vlc (String $status = "present") {

	package { 'vlc':
      ensure => installed,
    }

    file { "/etc/vlizedlab/startmenu.d/vlc":
      ensure => $status,
      source => "puppet:///modules/vlizedlab_v4/startmenustudentgui.static.vlc",
      require => [Package['vlc'], File["/etc/vlizedlab/startmenu.d"]]
    }

}
