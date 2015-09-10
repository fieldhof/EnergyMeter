<html>
<style type ="text/css">
body { color: #C8FA32; background-color: #003300; }
body { font-size: 14px;  font-family: Verdana; }
</style>
<body>
<h1>Electricity consumption / production</h1>


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

$query1 = 'SELECT tijd, vermogen FROM meting ORDER BY tijd DESC LIMIT 50';                                 // last houres, elke 10 seconde!

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
for ($data1 = array ();
    $row = mysql_fetch_array($result1);
    $data1[] = $row) {
}

echo ($data1[0][1] . "Watt");

//testing:


// data2[0][1] last consumption

mysql_free_result($result);
mysql_close($link);
//echo "End program";
?>  

</body>
</html>
