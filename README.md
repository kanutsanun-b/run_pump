# Run_pump version 0.0.1
!!!For Raspberry Pi zero, Automatic pump depen on humidity.

## Installation
```python
git clone https://github.com/kanutsanun-b/run_pump.git

#Pressure to Mean sea level ... QNH
pip install pressure2qnh

#BMP280
git clone https://github.com/pimoroni/enviro-phat.git
or
sudo apt-get install python3-envirophat
    "cd to the library directory, and run: sudo python3 setup.py install"
or
sudo pip3 install envirophat

#DHT22
git clone https://github.com/adafruit/Adafruit_Python_DHT.git
    "cd Adafruit_Python_DHT, and run: sudo python3 setup.py install"
or
sudo pip3 install Adafruit_DHT
```

## Usage
```python
Crontab...
@reboot sleep 60 && /home/pi/run_pump/run_project.py

index_rh = 47 #If Humidity is below than this value, pump will be started.
logfile = 'C:/Users/kanut/OneDrive/Documents_KB/python/RaspiZero_project/testlog/'
Latitude=10.72
station_height=13.657
```

## License
[MIT](https://choosealicense.com/licenses/mit/)

| ... | ... |
| ------ | ------ |
| email | kanutsanun.b@gmail.com |
| Build README | https://dillinger.io/ |