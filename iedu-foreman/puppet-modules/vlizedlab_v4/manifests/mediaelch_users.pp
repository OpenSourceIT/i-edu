class vlizedlab_v4::mediaelch_users {
	
	group { 'mediaelch-users':
		ensure => "present",
	}

	user { 'mediaelch1':
		ensure => "present",
		gid => "mediaelch-users",
		groups => ["mediaelch-users", "lp", "lpadmin", "media-music"],
		managehome => true,
		home => "/home/mediaelch1",
		shell => "/bin/bash",
		password => '$6$IgXyv5x6$inwsMXeRRAwxhbo7SruwGvAXes.3UnYiTIWUzVZqjN/ktkXq613CW1BjA5zXU6RA/6M1fouLIm/ZjIBHMlMh2/',
		require => Group['mediaelch-users'],
	}

	user { 'mediaelch2':
        ensure => "present",
        gid => "mediaelch-users",
        groups => ["mediaelch-users", "lp", "lpadmin", "media-music"],
        managehome => true,
        home => "/home/mediaelch2",
        shell => "/bin/bash",
        password => '$6$IgXyv5x6$inwsMXeRRAwxhbo7SruwGvAXes.3UnYiTIWUzVZqjN/ktkXq613CW1BjA5zXU6RA/6M1fouLIm/ZjIBHMlMh2/',
        require => Group['mediaelch-users'],
    }

	user { 'mediaelch3':
        ensure => "present",
        gid => "mediaelch-users",
        groups => ["mediaelch-users", "lp", "lpadmin", "media-music"],
        managehome => true,
        home => "/home/mediaelch3",
        shell => "/bin/bash",
        password => '$6$IgXyv5x6$inwsMXeRRAwxhbo7SruwGvAXes.3UnYiTIWUzVZqjN/ktkXq613CW1BjA5zXU6RA/6M1fouLIm/ZjIBHMlMh2/',
        require => Group['mediaelch-users'],
    }

	user { 'mediaelch4':
        ensure => "present",
        gid => "mediaelch-users",
        groups => ["mediaelch-users", "lp", "lpadmin", "media-music"],
        managehome => true,
        home => "/home/mediaelch4",
        shell => "/bin/bash",
        password => '$6$IgXyv5x6$inwsMXeRRAwxhbo7SruwGvAXes.3UnYiTIWUzVZqjN/ktkXq613CW1BjA5zXU6RA/6M1fouLIm/ZjIBHMlMh2/',
        require => Group['mediaelch-users'],
    }

	file { "/usr/local/bin/sync_mediaelch_profiles.sh":
		ensure => present,
		mode => '0755',
		source => "puppet:///modules/vlizedlab_v4/sync_mediaelch_profiles.sh",
    }

	cron { 'cron_sync_mediaelch_profiles':
		command => '/usr/local/bin/sync_mediaelch_profiles.sh',
		user    => 'root',
		hour    => 2,
		minute  => 0,
		require => [ Group['mediaelch-users'], File['/usr/local/bin/sync_mediaelch_profiles.sh'] ],
	}

}

