define vm::setting ($config, $status = "present")
{
	file { "/etc/vlizedlab/vm_setting.d/vm-$name":
      ensure => $status,
      content => template('vm/setting.erb'),
      require => File['/etc/vlizedlab/vm_setting.d'],
    }

}
