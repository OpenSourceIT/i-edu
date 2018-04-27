class vlizedlab_v4::chrome_profile {

    file { "/var/puppet-data/chrome-config.tar.gz":
      	ensure => present,
      	mode => '755',
      	source => "puppet:///modules/vlizedlab_v4/chrome-config.tar.gz",
		require => File['main-puppet-datadir'],
    }

    exec { "cmd-update-chrome-profile":
        command => "rm -r /home/student/.config/google-chrome; tar -xvf /var/puppet-data/chrome-config.tar.gz -C /home/student/.config/",
        path    => "/usr/bin/:/usr/sbin/:/bin/",
        refreshonly => true,
        subscribe => [
            File["/var/puppet-data/chrome-config.tar.gz"],
        ],
    }
}
