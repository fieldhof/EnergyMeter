<?php

$host = "localhost";
$user = "eneco";
$pass = "hallo";
$dbase = "energiedb";


$link = mysql_connect($host, $user, $pass);
if (!$link) {
	die('Could not connect: ' . mysql_error());
}
mysql_select_db($dbase, $link) or die('Could not select database.');

$query1 = 'SELECT * FROM meting24 ORDER BY time DESC';
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

$data1 = array();
while ($row = mysql_fetch_array($result1)) {
	$data1[] = $row;
}
mysql_free_result($result1);
mysql_close($link);
echo json_encode($data1);
?>
