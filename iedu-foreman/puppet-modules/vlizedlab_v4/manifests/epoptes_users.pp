class vlizedlab_v4::epoptes_users {
	
	group { 'epoptes-users':
		ensure => "present",
	}

	user { 'epoptes1':
		ensure => "present",
		gid => "epoptes-users",
		groups => ["epoptes", "lp", "lpadmin"],
		managehome => true,
		home => "/home/epoptes1",
		shell => "/bin/bash",
		password => '$6$IgXyv5x6$inwsMXeRRAwxhbo7SruwGvAXes.3UnYiTIWUzVZqjN/ktkXq613CW1BjA5zXU6RA/6M1fouLIm/ZjIBHMlMh2/',
		require => Group['epoptes-users'],
	}

	user { 'epoptes2':
        ensure => "present",
        gid => "epoptes-users",
        groups => ["epoptes", "lp", "lpadmin"],
        managehome => true,
        home => "/home/epoptes2",
        shell => "/bin/bash",
        password => '$6$IgXyv5x6$inwsMXeRRAwxhbo7SruwGvAXes.3UnYiTIWUzVZqjN/ktkXq613CW1BjA5zXU6RA/6M1fouLIm/ZjIBHMlMh2/',
        require => Group['epoptes-users'],
    }

	user { 'epoptes3':
        ensure => "present",
        gid => "epoptes-users",
        groups => ["epoptes", "lp", "lpadmin"],
        managehome => true,
        home => "/home/epoptes3",
        shell => "/bin/bash",
        password => '$6$IgXyv5x6$inwsMXeRRAwxhbo7SruwGvAXes.3UnYiTIWUzVZqjN/ktkXq613CW1BjA5zXU6RA/6M1fouLIm/ZjIBHMlMh2/',
        require => Group['epoptes-users'],
    }

	user { 'epoptes4':
        ensure => "present",
        gid => "epoptes-users",
        groups => ["epoptes", "lp", "lpadmin"],
        managehome => true,
        home => "/home/epoptes4",
        shell => "/bin/bash",
        password => '$6$IgXyv5x6$inwsMXeRRAwxhbo7SruwGvAXes.3UnYiTIWUzVZqjN/ktkXq613CW1BjA5zXU6RA/6M1fouLIm/ZjIBHMlMh2/',
        require => Group['epoptes-users'],
    }

	file { "/usr/local/bin/sync_epoptes_profiles.sh":
		ensure => present,
		mode => '0755',
		source => "puppet:///modules/vlizedlab_v4/sync_epoptes_profiles.sh",
    }

	cron { 'cron_sync_epoptes_profiles':
		command => '/usr/local/bin/sync_epoptes_profiles.sh',
		user    => 'root',
		hour    => 2,
		minute  => 0,
		require => [ Group['epoptes-users'], File['/usr/local/bin/sync_epoptes_profiles.sh'] ],
	}

}

