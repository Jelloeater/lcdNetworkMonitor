# Control LED on Pi w/ PRTG API

# Requirments
- sudo apt-get install python3-dev python3-smbus libi2c-dev -y
- I2C is enabled: On a Raspberry Pi, go to raspi-config, select Interfacing Options, then I2C, and choose Yes to enable it. Reboot your system afterward
- sudo raspi-config nonint do_i2c 0
- pip install -r requirements.txt --break-system-packages


** Don't forget to create a service**

``` 
root@lcd:/opt/lcdNetworkMonitor# cat /etc/systemd/system/lcd.service
[Unit]
Description=LCD Monitor
After=network.target

[Service]
Type=simple
Restart=always
RestartSec=1
User=root
ExecStart=python3 /opt/lcdNetworkMonitor/main.py

[Install]
WantedBy=multi-user.target
```