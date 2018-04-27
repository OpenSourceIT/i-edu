class vlizedlab_v4::kodi_profile {

    file { "/var/puppet-data/kodi-config.tar.gz":
      ensure => present,
      mode => 755,
      source => "puppet:///modules/vlizedlab_v4/kodi-config.tar.gz",
          require => Package["kodi"]
    }

    exec { "cmd-update-kodi-profile":
        command => "rm -r /home/student/.kodi; tar -xvzf /var/puppet-data/kodi-config.tar.gz -C /home/student/",
        path    => "/usr/bin/:/usr/sbin/:/bin/",
        refreshonly => true,
        subscribe => [
            File["/var/puppet-data/kodi-config.tar.gz"],
        ],
    }
}

