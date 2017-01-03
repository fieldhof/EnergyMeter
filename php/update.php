<?php

$host = "localhost";  //this is the raspberry pi on which the webserver and database is running
$user = "eneco";
$pass = "hallo";
$dbase = "energiedb";

$link = mysql_connect($host, $user, $pass);
if (!$link) {
    die('Could not connect: ' . mysql_error());
}
//echo 'Connected successfully<br>';

mysql_select_db($dbase, $link) or die('Could not select database.');

$query1 = 'SELECT * FROM meting ORDER BY time DESC LIMIT 1';                                 // last houres, elke 10 seconde!

//uitvoere0
$result1 = mysql_query($query1) or die(mysql_error()); 
if (!$result1) {
    echo "DB Error, could not query the database<br>";
    echo 'MySQL Error: ' . mysql_error();
    exit;
}

if (mysql_num_rows($result1) == 0) {
    echo "No rows found, nothing to print so am exiting<br>";
    exit;
}


//convert results to two dimensional array:

$data1 = mysql_fetch_array($result1);
echo ("<div class='page-header'>");
if(($data1[1]+$data1[2]) < 0) {
    echo ("<h2><font color='red'>" . ($data1[1]+$data1[2]) . "</font>");
} else {
    echo ("<h2><font color='green'>" . ($data1[1]+$data1[2]) . "</font>");
}
echo ("<small>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" . $data1[0] . "</small></h2></div>");

//testing:


// data2[0][1] last consumption

mysql_free_result($result);
mysql_close($link);
//echo "End program";
?>  
