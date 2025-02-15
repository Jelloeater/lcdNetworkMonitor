# Control LED on Pi w/ PRTG API

# Requirments
- sudo apt-get install python3-dev python3-smbus libi2c-dev -y
- I2C is enabled: On a Raspberry Pi, go to raspi-config, select Interfacing Options, then I2C, and choose Yes to enable it. Reboot your system afterward
- pip install git+https://github.com/jelloeater/displayotron.git@lib --break-system-packages
- uv run main.py
``` 

```