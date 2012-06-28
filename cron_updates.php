<?php

/*

UPDIAN - UpdateDebian v0.4

Minimalistic Debian Package Upgrade Tool with Web-Frontend by Robert Klikics, RobHost GmbH [rk@robhost.de], 2007-2012

License:    GPL
Web:        http://robhost.de/updian
File:       cron_updates.php - runs the desired updates from your install-queue or multi-ssh commands
Usage:      Should also run as cronjob, at least once a day ... recommended: every hour or something
	If there are no updates, it just does nothing, so don't panic ;)
		    
*/  


include 'config.php';

$dir = opendir($todo_dir);
$cnt = 0;
$srv = array();

// get servers first to get different port and other possible settings 
foreach(file($cfg_file) as $line) {

$srv_tmp = explode(":", trim($line));

// port
if( isset($srv_tmp[1]) ) {
    $port = $srv_tmp[1];
} else {
    $port = 22;
}

// engine
if( isset( $srv_tmp[2] ) && strtolower(trim($srv_tmp[2])) == 'yum') {
    $engine = 'yum';
} else {
    $engine = 'apt';
}

$srv[$srv_tmp[0]]['port'] = $port;
$srv[$srv_tmp[0]]['engine'] = $engine;
}

// loop through all files & update servers
while (false !== ($file = readdir($dir))) {

$log = "";

if ($file == "." || $file == "..")  continue;

$file = preg_replace("/\.txt$/", "", $file);
$ssh_port = $srv[$file]['port'];  // get SSH port
$engine = $srv[$file]['engine'];  // get packet manager

#var_dump($srv); exit;

echo "Host: $file, Port: $ssh_port, Engine: $engine\n";

// apt or yum?
if($engine == 'yum') {

// yum
$upd = "ssh -p $ssh_port $file '";
$upd.= "yum update -y --skip-broken'";
$done = `$upd`;
$log.= "$file (".date("M d, H:i")."):\n\n$done\n\n####################\n\n";        

// no checkrestart at this time for CentOS found :/

} else {

    // apt
    // set env-var DEBIAN_FRONTEND=noninteractive 
    // if we want to keep our existing cfg-files
    if($keep_cfgs)  $upd = "ssh -p $ssh_port $file 'export DEBIAN_FRONTEND=noninteractive && ";
    else            $upd = "ssh -p $ssh_port $file '";  

    $upd.= "apt-get upgrade -y'";
    $done = `$upd`; 
    exec("ssh -p $ssh_port $file apt-get autoclean");
    $log.= "$file (".date("M d, H:i")."):\n\n$done\n\n####################\n\n";

    // check if programs need to be restarted with checkrestart (deb-package: debian-goodies)
    $restart = "ssh -p $ssh_port $file checkrestart";
    $rs_out  = `$restart`;
    if( trim($rs_out) != "Found 0 processes using old versions of upgraded files") {

	// write checkrestart log
	$fp = fopen($log_path.$file."_checkrestart.log", "a");
	fwrite($fp, $rs_out, strlen($rs_out));
	fclose($fp);
	chmod($log_path.$file."_checkrestart.log", 0777); 
    }
}

// delete queue-file
unlink($todo_dir.$file.".txt");

// delete data-file
unlink($data_dir.$file.".txt");

// write logfile
$fp = fopen($log_path.$file.".log", "a");
fwrite($fp, $log, strlen($log));
fclose($fp);
chmod($log_path.$file.".log", 0777); // chmod 777 for delete from webserver

$cnt++;
}

// touch statfile
touch($data_dir."statfile_upd");

// output (local only)
if(!$cnt)   echo "No updates in queue (".date("H:i").") ...\n";
else        echo "Made $cnt updates (".date("H:i").")...\n";

// run multi-ssh command
if( file_exists($data_dir."multissh.txt") ) {

// get our cmd
$tmp = file($data_dir."multissh.txt");
$cmd = $tmp[0];
$log = "";

foreach(file($cfg_file) as $line) {

	$srv[] = explode(",", trim($line));
}

for($i = 0; $i < count($srv); $i++ ) {

#debug
echo $srv[$i][0]."\n";
    $log.= $srv[$i][0]." ";
            $do  = "ssh -l root ".$srv[$i][0]." 'export DEBIAN_FRONTEND=noninteractive && $cmd'";
            $res = `$do`;
            $log.= "$file (".date("M d, H:i")."):\n\n$res\n\n####################\n\n";
    }
 
    // write logfile
    $fp = fopen($log_path."multissh.log", "a");
    fwrite($fp, $log, strlen($log));
    fclose($fp);
    chmod($log_path."multissh.log", 0777); // chmod 777 for delete from webserver

    unlink($data_dir."multissh.txt");

    echo "Multi-SSH runned - $cmd - on ".count($srv)." machines (".date("H:i").")\n";
}

clearstatcache();

?>
