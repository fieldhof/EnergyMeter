# this program listens to the serial port of a P1 electricity Smart meter,
# receives the collected data en puts them into a mysql database
# juni 2015

import MySQLdb as mdb
import sys
import os
import time
import serial
import socket
from oled.device import ssd1306
from oled.render import canvas
from PIL import ImageFont
import commands

device = ssd1306(port=1, address=0x3C)

#Fonts
font1 = ImageFont.truetype("/var/www/ccra.ttf", 25)
font2 = ImageFont.truetype("/var/www/ccra.ttf", 35)


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
user = 'eneco'
password = 'hallo'
database = 'energiedb'

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
with canvas(device) as draw:
    draw.text((2,2), 'Starting', font=font1, fill=255)



try:
    ser.open()
    go = 1
except:
    with canvas(device) as draw:
	draw.text((2,2), 'Serial failed', font=font1, fill=255)

    sys.exit ("Error opening the serial port")
    go = 0

#================================================================
#=========== connect to mysql database1 =========================
#================================================================
# table name: meting
#================================================================
def writeToMeting():
	now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
	try:
		con = mdb.connect('localhost', 'eneco', 'hallo', 'energiedb')
       		with con:
			
       			cur = con.cursor()
			cur.execute("SELECT COUNT(*) FROM meting")
			size = cur.fetchone()[0]
			if size >= tablesize :
				rest = size - 359
				cur.execute("DELETE from meting WHERE time IS NOT NULL order by time asc LIMIT %s", rest)
                    	cur.execute("INSERT INTO meting(time,consumption,production) VALUES (%s,%s,%s)" ,( now, consumption, production))
                    	print now, "Data written in database "
                    	cur.close()
    	except ValueError:
     		print 'There is no connection with the database. Error ..'
	showMeting()


def writeToMeting24():
        print "Writing to 24 hour table"
        now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        try:
                con = mdb.connect('localhost', 'eneco', 'hallo', 'energiedb')
                with con:

                        cur = con.cursor()
                        cur.execute("SELECT COUNT(*) FROM meting24")
                        size = cur.fetchone()[0]
                        if size >= ((6*60*24)/dayprecision) :
                                rest = size - (tablesize - 1)
                                cur.execute("DELETE from meting24 WHERE time IS NOT NULL order by time asc LIMIT %s", rest)
                        cur.execute("INSERT INTO meting24(time,consumption,production) VALUES (%s,%s,%s)" ,( now, (conscount/dayprecision), (prodcount/dayprecision)))
                        cur.close()
        except ValueError:
                print 'There is no connection with the database. Error ..'



def showMeting():
	ip = commands.getoutput('ip address show dev eth0').split()
	ip = ip[ip.index('inet') + 1].split('/')[0]
	with canvas(device) as draw:
		padding = 2
		top = padding
		bottom = device.height - padding - 1
		draw.text((padding, top), ip, font=font1, fill=255)
		if consumption > 0 :
			draw.polygon([(8,26),(22,26),(22,40),(29,40),(15,59),(1,40),(8,40)], outline = 255,  fill=0)
			draw.text((padding+40, top+25), str(consumption), font=font2, fill=255)
		else :
			draw.polygon([(8,59),(22,59),(22,45),(29,45),(15,26),(1,45),(8,45)], outline = 255,  fill=0)
			draw.text((padding, top+25), str(production), font=font2, fill=255)
     
#===========================================
#==============    Main loop           =====
#===========================================

count = 0;
while True:
        #Read 1 line from serial port and analyse
        regel = str(ser.readline()).strip()
        if regel[0:9] == "1-0:1.8.1":
                totConsLow = float(regel[10:19])
                print "Totale verbruik (L) = ", totConsLow, " kW/h"
        elif regel[0:9] == "1-0:1.8.2":
                totConsHigh = float(regel[10:19])
                print "Totale verbruik (H) = ", totConsHigh, " kW/h"
        elif regel[0:9] == "1-0:2.8.1":
                totProdLow = int(float(regel[10:18])*1000)
                print "Totale productie (L) = ", totProdLow, " W/h"
        elif regel[0:9] == "1-0:2.8.2":
                totProdHigh = int(float(regel[10:18])*1000)
                print "Totale productie (H) = ", totProdHigh, " W/h"
        elif regel[0:9] == "1-0:1.7.0":
                consumption = int(float(regel[10:17])*1000)
                conscount += consumption
                print "Momentaan verbruik = ", consumption, " W/h"
        elif regel[0:9] == "1-0:2.7.0":
                production = int(float(regel[10:17])*1000)
                prodcount += production
                print "Momentaan production = ", production, " W/h"
        elif regel[0:10] == "0-1:24.3.0":
                newRegel = str(ser.readline()).strip()
                consGas = float(newRegel[1:10])
                print "Verbruik gas? = ", consGas, " m3"
        elif regel[0:1] == "!":
                count += 1
                count = count % dayprecision
                if not count :
                        writeToMeting24()
                        conscount = 0
                        prodcount = 0
                writeToMeting()
                print "\n"
        else:
                print regel


#end while go
#Close port and show status
try:
    ser.close()
except:
    sys.exit ("Program aborted. Serial port not closed.")
