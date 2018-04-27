class vlizedlab_v4::chromium_profile {

    file { "/var/puppet-data/chromium-config.tar":
      	ensure => present,
      	mode => '755',
      	source => "puppet:///modules/vlizedlab_v4/chromium-config.tar",
		require => File['main-puppet-datadir'],
    }

    exec { "cmd-update-chromium-profile":
        command => "rm -r /home/student/.config/chromium; tar -xvf /var/puppet-data/chromium-config.tar -C /home/student/",
        path    => "/usr/bin/:/usr/sbin/:/bin/",
        refreshonly => true,
        subscribe => [
            File["/var/puppet-data/chromium-config.tar"],
        ],
    }
}
