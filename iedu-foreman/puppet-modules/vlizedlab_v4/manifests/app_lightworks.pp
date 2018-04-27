class vlizedlab_v4::app_lightworks ($status = "present") {

    package { 'lightworks':
      ensure => installed,
    }

    file { "/etc/vlizedlab/startmenu.d/lightworks":
      ensure => $status,
      source => "puppet:///modules/vlizedlab_v4/startmenustudentgui.static.lightworks",
      require => Package['lightworks'],
    }

}
