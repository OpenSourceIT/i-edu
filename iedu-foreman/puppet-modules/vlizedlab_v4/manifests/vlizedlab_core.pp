class vlizedlab_v4::vlizedlab_core (Boolean $has_beamer = false, String $beamer_output = 'VGA1', Boolean $screensaver = false, Boolean $umountusb = true, Boolean $copycd = false) {

	file { 'main-puppet-datadir':
        name => '/var/puppet-data',
        ensure => 'directory',
    }

    package { 'htop':
      ensure => latest,
    }

    package { 'bwm-ng':
      ensure => latest,
    }

	package { 'ssh-askpass-gnome':
      ensure => installed,
    }

    file { "/usr/local/share/icons":
      ensure => directory,
    }

	if $::operatingsystem == 'Ubuntu' {
		package { 'google-chrome-stable':
      		ensure => latest,
    	}

		package { 'virtualbox-5.0':
            ensure => 'installed',
        }

		file { "/var/puppet-data/Oracle_VM_VirtualBox_Extension_Pack-5.0.40-115130.vbox-extpack":
            ensure => present,
            mode => '755',
            source => "puppet:///modules/vlizedlab_v4/Oracle_VM_VirtualBox_Extension_Pack-5.0.40-115130.vbox-extpack",
            require => Package['virtualbox-5.0'],
        }

		exec { "cmd-install-vbox-extpack-5.0":
            command => 'echo "y;" | VBoxManage extpack install /var/puppet-data/Oracle_VM_VirtualBox_Extension_Pack-5.0.40-115130.vbox-extpack',
            path    => "/usr/bin/:/usr/sbin/:/bin/",
            refreshonly => true,
            subscribe => [
                File["/var/puppet-data/Oracle_VM_VirtualBox_Extension_Pack-5.0.40-115130.vbox-extpack"],
	     	],
        }

		#package { 'virtualbox-5.2':
        #    ensure => 'installed',
        #}

        #file { "/var/puppet-data/Oracle_VM_VirtualBox_Extension_Pack-5.2.4-119785.vbox-extpack":
        #    ensure => present,
        #    mode => '755',
        #    source => "puppet:///modules/vlizedlab_v4/Oracle_VM_VirtualBox_Extension_Pack-5.2.4-119785.vbox-extpack",
        #    require => Package['virtualbox-5.2'],
        #}

        #exec { "cmd-install-vbox-extpack-5.2":
        #    command => 'echo "y;" | VBoxManage extpack install /var/puppet-data/Oracle_VM_VirtualBox_Extension_Pack-5.2.4-119785.vbox-extpack',
        #    path    => "/usr/bin/:/usr/sbin/:/bin/",
        #    refreshonly => true,
        #    subscribe => [
        #        File["/var/puppet-data/Oracle_VM_VirtualBox_Extension_Pack-5.2.4-119785.vbox-extpack"],
        #    ],
		#}

		file { "/etc/rc.local":
			ensure => present,
			mode => '0755',
			source => "puppet:///modules/vlizedlab_v4/rc.local-ubuntu",
			require => Package['iedu-client'],
		}

		file { "/etc/apt/preferences":
			ensure => present,
			source => "puppet:///modules/vlizedlab_v4/apt_preferences-ubuntu",
			before => Package['epoptes-client'],
		}

		file { "/etc/grub.d/10_linux":
			ensure => present,
			mode => '755',
			source => "puppet:///modules/vlizedlab_v4/grub_10_linux-ubuntu",
		}
	}

	if $::operatingsystem == 'Debian' {
        package { 'chromium':
            ensure => latest,
        }

		# Download latest version from: https://get.adobe.com/de/flashplayer/?no_redirect (Chrome Flash Plugin)
    	file { "/usr/lib/pepperflashplugin-nonfree/libpepflashplayer.so":
      		ensure => present,
      		mode => '0755',
      		source => "puppet:///modules/vlizedlab_v4/libpepflashplayer.so",
      		require => Package['pepperflashplugin-nonfree'],
    	}

		package { 'virtualbox':
      		ensure => '5.0.24-dfsg-2',
    	}

    	package { 'virtualbox-qt':
      		ensure => '5.0.24-dfsg-2',
    	}

    	package { 'virtualbox-dkms':
      		ensure => '5.0.24-dfsg-2',
    	}

    	file { "/etc/puppet/Oracle_VM_VirtualBox_Extension_Pack-5.0.24-108355.vbox-extpack":
      		ensure => present,
      		mode => '755',
      		source => "puppet:///modules/vlizedlab_v4/Oracle_VM_VirtualBox_Extension_Pack-5.0.24-108355.vbox-extpack",
      		require => Package['virtualbox'],
    	}

    	exec { "cmd-install-vbox-extpack":
        	command => "VBoxManage extpack install /etc/puppet/Oracle_VM_VirtualBox_Extension_Pack-5.0.24-108355.vbox-extpack",
        	path    => "/usr/bin/:/usr/sbin/:/bin/",
        	refreshonly => true,
        	subscribe => [
            	File["/etc/puppet/Oracle_VM_VirtualBox_Extension_Pack-5.0.24-108355.vbox-extpack"],
        	],
    	}

		file { "/etc/rc.local":
			ensure => present,
			mode => '0755',
			source => "puppet:///modules/vlizedlab_v4/rc.local",
			require => Package['iedu-client'],
		}

		file { "/etc/apt/preferences":
			ensure => present,
			source => "puppet:///modules/vlizedlab_v4/apt_preferences",
			before => Package['epoptes-client'],
		}

		file { "/lib/systemd/system/puppet.service":
			ensure => present,
			source => "puppet:///modules/vlizedlab_v4/puppet.service",
		}

		file { "/etc/grub.d/10_linux":
			ensure => present,
			mode => '755',
			source => "puppet:///modules/vlizedlab_v4/grub_10_linux",
		}

		package { 'pepperflashplugin-nonfree':
      		ensure => latest,
    	}
    }

	package { 'iedu-client':
      ensure => latest,
    }

    package { 'epoptes-client':
      ensure => installed,
    }

	package { 'ruby-augeas':
      ensure => installed,
    }

	group { 'vboxusers':
        ensure => "present",
    }

    user { 'student':
        ensure => "present",
        gid => "student",
        groups => ["audio", "vboxusers"],
	}

	package { 'iptables':
      ensure => absent,
    }

	file { "/etc/vlizedlab/startmenu.d":
      ensure => directory,
      require => Package['iedu-client'],
    }

	file { "/etc/vlizedlab/vm_usb_filter.d":
      ensure => directory,
      require => Package['iedu-client'],
    }

	file { "/etc/vlizedlab/vm_setting.d":
      ensure => directory,
      require => Package['iedu-client'],
    }

	#$has_beamer = false
    file { "/etc/vlizedlab/startmenustudentgui.ini":
      ensure => present,
      #source => "puppet:///modules/vlizedlab_v4/startmenustudentgui.ini",
	  content => template('vlizedlab_v4/startmenustudentgui.ini.erb'),
      require => Package['iedu-client'],
    }

    file { "/etc/vlizedlab/startmenustudentgui.static":
      ensure => present,
      source => "puppet:///modules/vlizedlab_v4/startmenustudentgui.static",
      require => Package['iedu-client'],
    }

	$sshkeys = hiera('ssh_authorized_keys')
    create_resources(ssh_authorized_key, $sshkeys)

    file { "/etc/apt/apt.conf.d/10periodic":
      ensure => present,
      mode => '755',
      source => "puppet:///modules/vlizedlab_v4/10periodic",
    }

    file { "/etc/default/grub":
      ensure => present,
      source => "puppet:///modules/vlizedlab_v4/grub_default",
    }

    file { "/etc/grub.d/40_custom":
      ensure => present,
      mode => '755',
      source => "puppet:///modules/vlizedlab_v4/grub_40_custom",
    }

    exec { "cmd-update-grub":
        command => "update-grub2",
        path    => "/usr/bin/:/usr/sbin/:/bin/",
        refreshonly => true,
        subscribe => [
            File["/etc/default/grub"],
            File["/etc/grub.d/10_linux"],
            File["/etc/grub.d/40_custom"],
        ],
    }

	file { "/etc/timezone":
      ensure => present,
      mode => '644',
      content => "Europe/Vienna",
    }

    file { '/etc/localtime':
       	ensure => 'link',
        target => '/usr/share/zoneinfo/Europe/Vienna',
    }

	file { "/usr/local/bin/repl_between_line.py":
    	ensure => present,
    	mode => '755',
    	source => "puppet:///modules/vlizedlab_v4/repl_between_line.py",
    }

	file { "/etc/systemd/logind.conf":
        ensure => present,
        mode => '644',
        source => "puppet:///modules/vlizedlab_v4/logind.conf",
    }
}
