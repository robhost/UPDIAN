<?php
/*

    UPDIAN - UpdateDebian v0.4

    Minimalistic Debian Package Upgrade Tool with Web-Frontend by Robert Klikics, RobHost GmbH [rk@robhost.de], 2007-2012

    License:    GPL
    Web:        http://robhost.de/updian
    File:       index.php - web frontend
    Usage:      open firefox/chrome/safari/lynx/whatever and call http://yourdomain/updian/ ;-)
    
*/  

// no-cache header
header("Expires: -1");
header("Cache-Control: post-check=0, pre-check=0");
header("Pragma: no-cache");
header("Last-Modified: " . gmdate("D, d M Y H:i:s") . " GMT");
?>
<html>
<head>
<title>Updian</title>
<script language="JavaScript">
function ask(url, txt) {

    if( confirm(txt) )  window.location = url;
}
function doIt() {

    if( confirm('This runs the given command on ALL your machines!\nAre you sure?') )  document.f1.submit();
}
</script>
<style>
body, td    { font: 12px verdana, arial; }
h1          { font: 24px verdana, arial; }
A:link      {text-decoration: none; color: dodgerblue}
A:visited   {text-decoration: none; color: dodgerblue}
A:active    {color: dodgerblue}
A:hover     {text-decoration: underline; color: dodgerblue}
.whiteTR    {background: #fff;}
.greyTR     {background: #cecece;}
</style>
<meta http-equiv="pragma" content="no-cache">
<body>
<h1>Updian - UpdateDebian v0.4</h1>
<h4>by <a href="http://www.robhost.de/updian/">RobHost GmbH</a>, 2007-<?=date(Y)?></h4>
hr>
<a href="index.php">Home</a> &nbsp;-&nbsp; <a href="index.php?act=queue">Queue</a> &nbsp;-&nbsp; <a href='index.php?act=servers'>Servers</a> &nbsp;-&nbsp; <a href='index.php?act=logs'>Logs</a> &nbsp;-&nbsp; <a href="index.php?act=ssh">Multi-SSH</a>
<hr>
<?php
include 'config.php';

// multi-ssh
if($_REQUEST[act] == "ssh") {

    echo "<h2>Multi-SSH</h1>";

    if( file_exists($data_dir."multissh.txt") ) {

        echo "multissh.txt exists, please run cron_updates.php or wait till the next cron-run..";
        echo "<br><br>Pending command:<br><i>"; 
        readfile($data_dir."multissh.txt");
        exit;
    }

    if( isset($_POST[run]) )    {

        if(empty($_POST[cmd]))   die("No cmd given ..");

        $res = escapeshellcmd($_POST['cmd']);

        // write statusfile in $data_dir
        $fp = fopen($data_dir."multissh.txt", "w");
        fwrite($fp, $res, strlen($res));
        fclose($fp);

        echo "Saved! Now please run cron_updates.php as root or wait till the next cron-run.<br>The output will be logged (see <i>Logs</i>).<br><br>The command was:<br><br><i>$res</i><br><br>";

        die("<br><br></body></html>");
    }

    echo "With <i>Multi-SSH</i> you can run any shell-command <b>once</b> on <b>all</b> your machines!";
    echo "<br><br>";
    echo "<form action='index.php' method='post' name='f1'>\n";
    echo "<input type='hidden' name='act' value='ssh'>\n";
    echo "<input type='hidden' name='run' value='1'>\n";
    echo "The command:<br><input type='text' name='cmd' size='50'>\n";
    echo "<input type='button' value='run command' onClick='javascript:doIt()'>";

    die("<br><br></body></html>");
}


// show|edit server-list

if($_REQUEST[act] == "servers") {

    if( isset($_POST[save]) ) {

        // save new $cfg_file
        $fp = fopen($cfg_file, "w") or die("Could not open $cfg_file for writing ...");
        $postdata = trim($_POST[txt]) . "\n";
        @fwrite($fp, $postdata, strlen($postdata));
        @fclose($fp);
    }

    #$cmd = "cat $cfg_file";
    #$srv = `$cmd`;
    #$row = count( file($cfg_file) );  // calculate rows for textarea
    $file = file($cfg_file);
    $row  = count($file) + 2;
    $srvs = '';
    sort($file);

    foreach($file as $srv) {
        if( trim($srv) == "") {
            continue;
        }
        $srvs.= $srv;
    }

    $srvs.= "\n";

    echo "<h3>View/Edit <i>$cfg_file</i>:</h3>(one host per line, optional :portnumber after hostname if SSH not on 22)<br><br>";
    echo "<form action='index.php' method='post'>\n";
    echo "<input type='hidden' name='act' value='servers'>\n";
    echo "<input type='hidden' name='save' value='1'>\n";
    echo "<textarea style='border:1px solid black;padding:5px;' name='txt' rows='$row' cols='50'>$srvs</textarea>\n";
    echo "<br><br><input type='submit' value='Save to $cfg_file'>\n";
    echo "</form>\n";
    
    die("<br><br></body></html>");
}


// add to queue
if($_GET[act] == "add") {

    if( $_GET[all_servers] == 1 )   { 

        // add ALL
        $dir = opendir($data_dir);
        while (false !== ($file = readdir($dir))) {

            if ($file == "." || $file == "..")  continue;
            if($file == "statfile")             continue;
            if($file == "statfile_upd")         continue;

            if(!file_exists($todo_dir.$file))   touch($todo_dir.$file);
        }
        
    } else {
        
        touch($todo_dir.$_GET[srv].".txt");  // add unique server
    }
}

// view logs
if($_GET[act] == "logs") {

    if( isset($_GET[del]) ) {

        // del all?
        if($_GET[del] == "all") {
            
            $dir = opendir($log_path);

            while (false !== ($file = readdir($dir))) {

                if ($file == "." || $file == "..")  continue;
                @unlink($log_path.$file);
            }

        } else {

            // del unique logfile    
            @unlink($log_path.$_GET[del]);
        }
    }

    $dir = opendir($log_path);
    $cnt = 0;
    $logs = array();

    echo "<h3>Logfiles</h3>";
    echo "<table width='600' cellspacing='0' cellpadding='2'>\n";

    while (false !== ($file = readdir($dir))) {

        if ($file == "." || $file == "..")  continue;

        $logs[] = $file;
        $cnt++;   
     }

    sort($logs);

    foreach($logs as $files) {
        if(preg_match("/checkrestart/", $files))
            $col = "yellow";
        else
            $col = "";

        echo "<tr onmouseover=\"this.className='greyTR';\" onmouseout=\"this.className='whiteTR';\"><td><a href='".$log_path_rel.$files."'><span style='background:$col'>$files</a> </td><td>".date("M d, H:i", filemtime($log_path.$files))."</td><td align='right'><a href='javascript:ask(\"index.php?act=logs&del=$files\", \"Delete $files?\")'>delete</a></td></tr>\n";
    }

    echo "</table>";

    if(!$cnt)   echo "Logdir is empty ...";
    if($cnt)    echo "<br><br><a href='javascript:ask(\"index.php?act=logs&del=all\",\"Really?\")'>Delete ALL logs</a>";
    die("<br/><br/></body></html>");
}

// show queue
if($_GET[act] == "queue") {

    // are we going to del a server from the queue?
    if( isset($_GET[del]) ) {

        @unlink($todo_dir.$_GET[del].".txt");
    }


    // show servers in $todo_dir
    echo "UpdateCronjob last runtime: ".date ("F d Y H:i.", @filemtime($data_dir."statfile_upd"));
    echo "<br>";
    echo "<h3>Servers in queue - will be updated on next cron-run</h3>";
    echo "<table width='600' cellspacing='0' cellpadding='2'>\n";

    $dir = opendir($todo_dir);
    $cnt = 0;
    $que = array();

    while (false !== ($file = readdir($dir))) {

        if ($file == "." || $file == "..")  continue;
        $file = preg_replace("/\.txt$/", "", $file);
    
        $que[] = "<tr onmouseover=\"this.className='greyTR';\" onmouseout=\"this.className='whiteTR';\"><td>" . $file."</td><td>queued: ".date("M d, H:i", filemtime($todo_dir.$file.".txt"))."</td><td align='right'><a href='javascript:ask(\"index.php?act=queue&del=$file\", \"Delete $file from queue?\")'>delete</a></td></tr>";
        $cnt++;
    }

    sort($que);

    foreach($que as $que_entry) {
        echo $que_entry;
    }

    echo "</table>";

    if(!$cnt)   echo "Currently no servers in queue ...";

    die("</body></html>");
}


// print info on index page
echo "Data collected on: ".date ("F d Y H:i.",@filemtime($data_dir."statfile"))."<br>";
echo "<h3>Updates available:</h3>";

$dir = opendir($data_dir);
$mcnt = 0;
$_html = array();
$_tmp_html = '';

echo "<table width='600' cellspacing='0' cellpadding='2'>\n";
// get info for all servers from datadir
while (false !== ($file = readdir($dir))) {
    
    if ($file == "." || $file == "..")  continue;
    if($file == "statfile")             continue;
    if($file == "statfile_upd")         continue;
    if($file == "multissh.txt")         continue;

    $cnt  = count( file($data_dir.$file) );
    $file = preg_replace("/\.txt$/", "", $file);

    $_tmp_html =  "\n<tr onmouseover=\"this.className='greyTR';\" onmouseout=\"this.className='whiteTR';\"><td>$file</td><td align='center'><a href='index.php?act=show&srv=$file#updates' title='show packages'>$cnt updates</a></td><td align='right'>";

    if(!file_exists($todo_dir.$file.".txt"))    $_tmp_html.= "<a href='javascript:ask(\"index.php?act=add&srv=$file\", \"Install updates for $file when install-cronjob runs next time?\")'>add to queue</a>";
    else                                        $_tmp_html.= "queued";

    $_tmp_html.= '</td></tr>';

    $_html[] = $_tmp_html;

    $mcnt++;
}

sort($_html);

foreach($_html as $line) {
    echo $line;
}


echo "</table>";
if($cnt) echo "<br><br><li><a href='javascript:ask(\"index.php?act=add&all_servers=1\",\"Add all updates on all $mcnt servers to the queue?\")'>Add all $mcnt servers to install-queue</a>";
if(!$cnt)   echo "Currently no pending updates ...";
echo "<br><a name='updates'></a>";

// show off updates
if($_GET[act] == "show") {

    $toshow  = $data_dir.$_GET[srv].".txt";
    $content = `cat $toshow`;

    echo "<h3>Updates for $_GET[srv]";
    
    if(!file_exists($todo_dir.$_GET[srv].".txt"))   echo " [ <a href='javascript:ask(\"index.php?act=add&srv=$_GET[srv]\", \"Install updates for $_GET[srv] when install-cronjob runs next time?\")'>add to install-queue</a> ]</h3>";
    else                                            echo "</h3>";

    $content = preg_replace("/Inst |base|updates/", "", $content);
   
    echo nl2br($content);
    echo "<br><br><li><a href='javascript:scroll(0,0)'>top</a><br><br>";

}

clearstatcache();

?>



</body>
</html>
