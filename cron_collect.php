<?php

/*

    UPDIAN - UpdateDebian v0.4

    Minimalistic Debian Package Upgrade Tool with Web-Frontend by Robert Klikics, RobHost GmbH [rk@robhost.de], 2007-2012
 
    License:    GPL
    Web:        http://robhost.de/updian
    File:       cron_collect.php - collects update-data from all servers
    Usage:      Should be run as cronjob once or twice a day

*/

include 'config.php';

$srv = array();

// clean datadir in advance
@system("rm ".$data_dir."*.txt");

// split by ":"
foreach(file($cfg_file) as $line) {

    $srv[] = explode(":", trim($line));
}

$mailtxt = "";

for($i = 0; $i < count($srv); $i++ ) {

    // get ssh port
    if( isset( $srv[$i][1] ) && is_numeric($srv[$i][1]) ) {
        $port = trim($srv[$i][1]);
    } else {
        $port = 22;
    }

    // local output, for information only 
    if( isset( $srv[$i][2] ) && strtolower(trim($srv[$i][2])) == 'yum') {
    	$engine = 'yum';
    } else {
	$engine = 'apt';
    }

    echo "Query: ".$srv[$i][0].", Port ".$port.", Engine: $engine \n";

    // apt or yum?
    if($engine == 'yum') {
	
	$upd = "ssh -l root -p ".$port." ".$srv[$i][0]." yum check-update -q";

    } else {
	
	// apt
    	exec("ssh -l root -p ".$port." ".$srv[$i][0]." apt-get autoclean -y");
    	system("ssh -l root -p ".$port." ".$srv[$i][0]." apt-get update -qq");  // qq = quiet
    	$upd = "ssh -l root -p ".$port." ".$srv[$i][0]." apt-get upgrade -s | grep Inst"; // s = simulate!
    }

    $res = `$upd`;
    $res = preg_replace("/(^[\r\n]*|[\r\n]+)[\s\t]*[\r\n]+/", '', $res);  // remove empty lines

    if( trim($res) == "")   continue;  // next if empty result

    // write statusfile in $data_dir
    $fp = fopen($data_dir.$srv[$i][0].".txt", "w");
    fwrite($fp, $res, strlen($res));
    fclose($fp);

    if($mail_active) {

        $num = count( explode("\n", $res) ) - 1;
        $mailtxt.= $srv[$i][0].": $num pending updates\n"; 
    }
}

// write statusfile
touch($data_dir."statfile");

// send mail (if wanted only)
if($mailtxt) {
    
    $cnt     = count( explode("\n", $mailtxt) ) -1 ;
    $subject = "[updian] $cnt servers with updates pending!";
    $txt     = "Updian has detected that the following servers have pending updates:\n\n$mailtxt\n\nYou can manage these updates under $updian_uri\n\nRegards,\nupdian on ".`hostname -f`;

    mail($mail_to, $subject, $txt, "From: updian <".$mail_from.">");

    echo "Mail sent to $mail_to\n";
}

?>




