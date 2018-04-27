class vlizedlab_v4::i3_config (String $version, String $content) {

	$i3config = "/home/student/.config/i3/config"

	exec { "update-i3-config":
        command => "/usr/local/bin/repl_between_line.py '${i3config}' '##foreman:v' '##foreman:end##' && echo '\n\n##foreman:v${version}##\n$content\n##foreman:end##' >> ${i3config}",
        path    => "/usr/bin/:/usr/sbin/:/bin/",
        unless  => "grep '##foreman:v$version##' ${i3config}",
		require => File["/usr/local/bin/repl_between_line.py"],
    }

}
