<?php

/*
    UPDIAN - UpdateDebian

    Minimalistic Debian Package Upgrade Tool with Web-Frontend by Robert Klikics, RobHost GmbH [rk@robhost.de], 2007-2013

    License:    GPL
    Web:        http://robhost.de/updian
    File:       config.php - setup
    Usage:      Edit the vars as needed
*/  


// general options
$cfg_file  = "/var/www/updian/server.txt";  // file with server-infos
$data_dir  = "/var/www/updian/data/";       // storage-dir for infos, keep "/" at the end!
$todo_dir  = "/var/www/updian/todo/";       // storage-dir for updates in queue, keep "/" at the end!
$log_path  = "/var/www/updian/log/";        // path to logfilem, please keep "/"
$log_path_rel = "./log/";    // path to lofiles relative to the webdir, keep "/"


// update-options
$keep_cfgs = true;  /* true or false. if true, Updian ALWAYS KEEPS YOUR EXISTING CONFIGS in case of package-upgrades with configfile-changes.
                      if false, Updian possibly crashes or hangs when the client is asking for what to do with the existing cfg-files (overwrite/cancel/leave)!!
                      TRUE IS HIGHLY RECOMMENDED AND RUNS WITHOUT PROBLEMS IN MOST CASES!!!    
                    */  


// uri to you installation (for hyperlink in mails i.e.)
$updian_uri= "http://192.168.0.254/updian/";

// mail options
$mail_active = true;                    // send infomails: true|false
$mail_to     = "server@domain.tld";     // To: for infomails, should be your valid email (mail1[,mail2])
$mail_from   = "updian@domain.tld";     // From: for mail, default: updian@yourhost.tld, have a look at "hostname -f"

// concurrency options (Python backend)
$concurrency = 20;

// backend auto-detection
$autodetect_backend = true;

// allow unauthenticated packages
$allow_unauthenticated_packages = false;

?>
