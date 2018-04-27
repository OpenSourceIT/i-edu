$vl_hostname = "vsrv-iedu-server"
$vl_hostip = "10.70.101.2"
$vl_hostip_mask = "24"
$vl_hostgateway = "10.70.101.254"
$vl_hostdns = "10.70.101.1"
$vl_nicname = "Kabelnetzwerkverbindung 2"

$foreman_host = "10.70.101.1"
$foreman_user = "api"
$foreman_pass = "zfWr6DYlwOuVkVK"

class installer {

  exec { "set_hostname":
    command => "hostnamectl set-hostname $vl_hostname",
    path    => "/usr/bin/:/usr/sbin/:/bin/",
    unless  => "/usr/bin/test '$vl_hostname' = `hostnamectl status | grep hostname | cut -d: -f2 | cut -d' ' -f2`",
  }

  augeas { "set_hosts":
    context => "/files/etc/hosts",
    changes => [
      "set *[ipaddr = '127.0.1.1']/canonical $vl_hostname",
    ],
  }

  exec { "set_ip_addr":
    command => "nmcli connection modify id '$vl_nicname' ipv4.addresses $vl_hostip/$vl_hostip_mask",
    path    => "/usr/bin/:/usr/sbin/:/bin/",
    unless  => "/usr/bin/test '$vl_hostip/$vl_hostip_mask' = `cat '/etc/NetworkManager/system-connections/$vl_nicname' | grep address1 | cut -d= -f2 | cut -d, -f1`",
  }

  exec { "set_ip_gateway":
    command => "nmcli connection modify id '$vl_nicname' ipv4.gateway $vl_hostgateway",
    path    => "/usr/bin/:/usr/sbin/:/bin/",
    unless  => "/usr/bin/test '$vl_hostgateway' = `cat '/etc/NetworkManager/system-connections/$vl_nicname' | grep address1 | cut -d= -f2 | cut -d, -f2`",
  }

  exec { "set_ip_dns":
    command => "nmcli connection modify id '$vl_nicname' ipv4.dns $vl_hostdns",
    path    => "/usr/bin/:/usr/sbin/:/bin/",
    unless  => "/usr/bin/test '$vl_hostdns' = `cat '/etc/NetworkManager/system-connections/$vl_nicname' | grep dns= | cut -d= -f2 | cut -d';' -f1`",
  }

  exec { "set_foreman_host":
    command => "sed -i 's/^FOREMAN_HOST = .*/FOREMAN_HOST = $foreman_host/' /etc/iedu-server/config",
    path    => "/usr/bin/:/usr/sbin/:/bin/",
  }

  exec { "set_foreman_user":
    command => "sed -i 's/^FOREMAN_USER = .*/FOREMAN_USER = $foreman_user/' /etc/iedu-server/config",
    path    => "/usr/bin/:/usr/sbin/:/bin/",
  }

  exec { "set_foreman_pass":
    command => "sed -i 's/^FOREMAN_PASS = .*/FOREMAN_PASS = $foreman_pass/' /etc/iedu-server/config",
    path    => "/usr/bin/:/usr/sbin/:/bin/",
  }

}

include installer

