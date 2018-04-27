class vlizedlab_v4::zentral_download {

	unless File["cifs-utils"] {
		file { 'cifs-utils':
			status => 'installed',
		}
	}

	file { 'download-zentral-dir':
        name => '/home/student/Downloads',
        ensure => 'directory',
    }

    mount { 'download-zentral':
      	ensure => mounted,
	  	name => "/home/student/Downloads",
	  	device => "//vsrv-dom.nmsruprecht.local/downloads-zentral",
	  	fstype => "cifs",
	  	options => "credentials=/root/.smbcredentials,_netdev,users,auto,vers=3.0,uid=student",
	  	require => [ File["/root/.smbcredentials"], File["download-zentral-dir"] ]
    }

	file { "/root/.smbcredentials":
      	ensure => present,
      	mode => '0600',
      	source => "puppet:///modules/vlizedlab_v4/zentral_download_smbcredentials.conf",
    }

}
