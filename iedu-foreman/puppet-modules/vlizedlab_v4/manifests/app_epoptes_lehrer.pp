class vlizedlab_v4::app_epoptes_lehrer (String $sshuser = 'student', String $status = "present") {

	$str_cmd = "#!/bin/bash
#SSH_ASKPASS=/usr/bin/ssh-askpass-fullscreen
ssh $sshuser@vsrv-vlizedlab.nmsruprecht.local -X epoptes
"

    file { "/usr/local/bin/startepoptes":
      ensure => $status,
      mode => '755',
	  content => $str_cmd,
    }

    file { "/usr/local/share/icons/epoptes_logo.png":
      ensure => $status,
      mode => '644',
      source => "puppet:///modules/vlizedlab_v4/epoptes_logo.png",
	  require => File["/etc/vlizedlab/startmenu.d"]
    }

    file { "/etc/vlizedlab/startmenu.d/epoptes-management":
      ensure => $status,
      source => "puppet:///modules/vlizedlab_v4/startmenustudentgui.static.epoptes-lehrer",
	  require => [Package['ssh-askpass-gnome'], File["/etc/vlizedlab/startmenu.d"]]
    }

}

