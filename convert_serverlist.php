<?php
/*

    UPDIAN - UpdateDebian v0.4

    Minimalistic Debian Package Upgrade Tool with Web-Frontend by Robert Klikics, RobHost GmbH [rk@robhost.de], 2007-2013

    License:    GPL
    Web:        http://robhost.de/updian
    File:       convert_serverlist.php - convert old server.txt to new JSON encoded server.json
    Author:     Dirk Dankhoff [dd@robhost.de]
    Usage:      open firefox/chrome/safari/lynx/whatever and call http://yourdomain/updian/ ;-)

*/

include 'config.php';

$extensions = explode('.', $cfg_file);
$extension = array_pop($extensions);

if ($extension === 'json') {
    die('Serverlist was apparently already converted to JSON ($cfg_file has .json-extension in config.php). Aborting.');
}

$data = file($cfg_file);
$serverlist = array();

echo 'Converting...' . PHP_EOL;

foreach ($data as $line) {
    $line = trim($line);
    $server_data = explode(':', $line);

    $s = array('hostname' => array_shift($server_data));

    if (count($server_data)) {
        $s['port'] = intval(array_shift($server_data));

        // omit standard port, most likely just set in order to specify a backend
        if ($s['port'] == 22)
            unset($s['port']);
    }

    if (count($server_data)) {
        $s['backend'] = array_shift($server_data);

        // do not omit standard backend here;
        // if it exists it was set explicitly by the user
    }

    if (count($server_data)) {
        die(sprintf('Found unknown amount of server metadata: %d.', count($server_data)));
    }

    $serverlist[] = $s;
}

$extensions[] = 'json';
$new_name = implode('.', $extensions);

// add additional suffix if file already exists to prevent accidental overwriting
if (file_exists($new_name)) {
    $new_name .= '.convnew';
}

echo 'Saving to file ' . $new_name . '.' . PHP_EOL;
file_put_contents($new_name, json_encode($serverlist));

echo 'Now please check the converted file and adjust your config.php accordingly.' . PHP_EOL;

echo 'Done.' . PHP_EOL;
