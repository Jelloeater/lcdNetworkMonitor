# Control LED on Pi w/ PRTG API

# Requirments
- sudo apt-get install python3-dev python3-smbus libi2c-dev -y
- I2C is enabled: On a Raspberry Pi, go to raspi-config, select Interfacing Options, then I2C, and choose Yes to enable it. Reboot your system afterward
- sudo raspi-config nonint do_i2c 0
- pip install -r requirements.txt --break-system-packages
- pip3 install ping3 --break-system-packages
- uv run main.py
``` 

```