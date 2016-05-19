# EnergyMeter
Raspi energy consumption meter

1. edit `/etc/inittab` so `T0:23:respawn:/sbin/getty -L ttyAMA0 115200 vt100` is commented out with a `#`
2. edit `/boot/cmdline.txt` and remove all references to `ttyAMA0`
3. do an `apt-get update`
4. `apt-get install python-serial mysql-server python-mysqldb apache2 php5 php5-mysql php5-gd`
5. `cd /var/www/`
6. `git clone https://github.com/fieldhof/EnergyMeter.git`
7. `python /var/www/energy.py`
8. go the ip address of your pi in a browser

##Optional
9. To start the energymonitor at reboot `crontab -e` and add the line `@reboot python /var/www/energy.py` 
