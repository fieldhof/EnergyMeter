# EnergyMeter
Raspi energy consumption meter

1. edit /etc/inittab so T0:23:respawn:/sbin/getty -L ttyAMA0 115200 vt100 is commented out with a ' # '
2. edit /boot/cmdline.txt and remove all references to ttyAMA0
3. do an apt-get update
4. install python-serial, mysql-server, python-mysqldb, apache2, php5, php5-mysql, php5-gd
5. put the index.php and energy.py in /var/www
6. start energy.py with python and wait a bit
7. go the ip address of your pi in a browser
