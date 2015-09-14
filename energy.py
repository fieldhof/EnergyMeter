# python program: p1spanje04.py
# this program listens to the serial port of a P1 electricity Smart meter,
# receives the collected data en puts them into a mysql database
# Lent, Netherlands
# Z.E.H. Otten
# juni 2015

import MySQLdb as mdb
import sys
import os
import time
import serial

#===========================================
#========== init values/parameters ====
#===========================================
version="energy.py"
os.environ['TZ'] = 'Europe/Amsterdam'
now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
db = "true" 
go = "false"

#variables used:
dag = str(6) #Production in W
nacht = str(6)
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
    go = "true"
except:
    sys.exit ("Error opening the serial port")
    go = "false"

#================================================================
#=========== connect to mysql database1 =========================
#================================================================
# table name: metingen2
# delete one measurement 
# and insert one new measurement
# so the table does not grow infinite
#================================================================
def writeToMeting():
    now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    try:
       con = mdb.connect('localhost', 'eneco', 'hallo', 'energiedb')
       db="true"
       with con:
                    cur = con.cursor()
                    cur.execute("DELETE from meting order by tijd ASC LIMIT 1")
                    cur.execute("INSERT INTO meting(tijd,dag,nacht) VALUES (%s,%s,%s)" ,( now, dag, nacht))
                    print now, "Data written in database "
                    cur.close()
    except ValueError:
     print 'There is no connection with the database. Error ..'
     db="false"
     
#===========================================
#==============    Main loop           =====
#===========================================
print ("energy.py",  version)
print ("Control-C om to stop the program")
print "Time: ",now
t = time.time()
old1 = 0; dW = 0; W = 0; count = 0;
while go == "true": 
     # the P1 electricity Smart meter produces 15 data lines (regel)
     for x in range(1,16):
        regel=''
        #Read 1 line from serial port and analyse
        regel = ser.readline()
        regel=str(regel)
        regel=regel.strip()
        if regel[0:9] == "1-0:2.7.0":
             dag = str(int(float(regel[10:17])*1000))
        elif regel[0:9] == "1-0:1.7.0":
             nacht = str(int(float(regel[10:17])*1000))
     writeToMeting()

#end while go
#Close port and show status
try:
    ser.close()
except:
    sys.exit ("Program aborted. Serial port not closed.")
