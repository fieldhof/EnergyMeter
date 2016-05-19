# this program listens to the serial port of a P1 electricity Smart meter,
# receives the collected data en puts them into a mysql database
# juni 2015

import MySQLdb as mdb
import sys
import os
import time
import serial
import socket
import commands
from warnings import filterwarnings
filterwarnings('ignore', category = mdb.Warning)

#===========================================
#========== init values/parameters ====
#===========================================
version="energy.py"
os.environ['TZ'] = 'Europe/Amsterdam'
now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

#variables used:
production = 0 	#Production in W
consumption = 0	#Consumption in W

prodcount = 0
conscount = 0

tablesize = 360
dayprecision = 12

host = 'localhost'
user = 'root'
password = 'hallo'
database = "energiedb"

try:
    db = mdb.connect(host, user, password)
    cur = db.cursor()
    cur.execute("CREATE DATABASE IF NOT EXISTS %s" % database)
    cur.execute("use %s" % database)
    cur.execute("CREATE TABLE IF NOT EXISTS meting (time datetime, consumption int(3), production int(3))")
    cur.execute("CREATE TABLE IF NOT EXISTS meting24 (time datetime, consumption int(3), production int(3))")
except ValueError:
    print "Something went wrong connecting to database"
#Set COM port config
ser = serial.Serial()
ser.baudrate = 9600
ser.bytesize=serial.SEVENBITS
ser.parity=serial.PARITY_EVEN
ser.stopbits=serial.STOPBITS_ONE
ser.xonxoff=0
ser.rtscts=0
ser.timeout=20
ser.port="/dev/ttyAMA0"

#===========================================
#============== connect to serial port =====
#===========================================
#Open COM port
try:
    ser.open()
    go = 1
except:
    sys.exit ("Error opening the serial port")
    go = 0

#================================================================
#=========== connect to mysql database1 =========================
#================================================================
# table name: meting
#================================================================
def writeToMeting():
#    print "Writing to database"
    now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    try:
        con = mdb.connect(host, user, password, database)
 	cur = con.cursor()
	cur.execute("SELECT COUNT(*) FROM meting")
	size = cur.fetchone()[0]
	if size >= tablesize :
	    rest = size - 359
	    cur.execute("DELETE from meting WHERE time IS NOT NULL order by time asc LIMIT %s" , rest)
	    cur.execute("INSERT INTO meting(time,consumption,production) VALUES (%s,%s,%s)" ,(now, consumption, production))
            con.commit()
	    print now, "Data written in database "
            cur.close()
    except ValueError:
     	print 'There is no connection with the database. Error ..'


def writeToMeting24():
#    print "Writing to 24 hour table"
    now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    try:
        con = mdb.connect(host, user, password, database)
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM meting24")
        size = cur.fetchone()[0]
        if size >= ((6*60*24)/dayprecision) :
            rest = size - (tablesize - 1)
            cur.execute("DELETE from meting24 WHERE time IS NOT NULL order by time asc LIMIT %s" , rest)
            cur.execute("INSERT INTO meting24(time,consumption,production) VALUES (%s,%s,%s)" , ( now, (conscount/dayprecision), (prodcount/dayprecision)))
            con.commit()
            cur.close()
    except ValueError:
        print 'There is no connection with the database. Error ..'

#===========================================
#==============    Main loop           =====
#===========================================

count = 0;
while True:
    #Read 1 line from serial port and analyse
    regel = str(ser.readline()).strip()
    if regel[0:9] == "1-0:1.8.1":
        totConsLow = float(regel[10:19])
#        print "Totale verbruik (L) = ", totConsLow, " kW/h"
    elif regel[0:9] == "1-0:1.8.2":
        totConsHigh = float(regel[10:19])
#        print "Totale verbruik (H) = ", totConsHigh, " kW/h"
    elif regel[0:9] == "1-0:2.8.1":
        totProdLow = int(float(regel[10:18])*1000)
#        print "Totale productie (L) = ", totProdLow, " W/h"
    elif regel[0:9] == "1-0:2.8.2":
        totProdHigh = int(float(regel[10:18])*1000)
#        print "Totale productie (H) = ", totProdHigh, " W/h"
    elif regel[0:9] == "1-0:1.7.0":
        consumption = int(float(regel[10:17])*1000)
        conscount += consumption
#        print "Momentaan verbruik = ", consumption, " W/h"
    elif regel[0:9] == "1-0:2.7.0":
        production = int(float(regel[10:17])*1000)
        prodcount += production
#        print "Momentaan production = ", production, " W/h"
    elif regel[0:10] == "0-1:24.3.0":
        newRegel = str(ser.readline()).strip()
        consGas = float(newRegel[1:10])
#        print "Verbruik gas? = ", consGas, " m3"
    elif regel[0:1] == "!":
        count += 1
        count = count % dayprecision
        if not count :
            writeToMeting24()
            conscount = 0
            prodcount = 0
        writeToMeting()
#        print "\n"
    else:
#        print regel


#end while go
#Close port and show status
try:
    ser.close()
except:
    sys.exit ("Program aborted. Serial port not closed.")
