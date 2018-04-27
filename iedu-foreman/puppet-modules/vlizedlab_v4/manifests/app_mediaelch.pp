class vlizedlab_v4::app_mediaelch (String $sshuser = 'student', String $status = "present") {


	$str_cmd = "#!/bin/bash
#SSH_ASKPASS=/usr/bin/ssh-askpass-fullscreen
ssh $sshuser@vsrv-vlizedlab.nmsruprecht.local -X MediaElch
"

    file { "/usr/local/bin/startmediaelch":
      ensure => $status,
      mode => '755',
	  content => $str_cmd,
    }

    file { "/usr/local/share/icons/mediaelch_logo.png":
      ensure => $status,
      mode => '644',
      source => "puppet:///modules/vlizedlab_v4/mediaelch_logo.png",
	  require => File["/etc/vlizedlab/startmenu.d"]
    }

    file { "/etc/vlizedlab/startmenu.d/mediaelch-management":
      ensure => $status,
      source => "puppet:///modules/vlizedlab_v4/startmenustudentgui.static.mediaelch",
	  require => [Package['ssh-askpass-gnome'], File["/etc/vlizedlab/startmenu.d"]]
    }

}

