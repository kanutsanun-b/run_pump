import lcddriver
import time
import csv
from datetime import datetime
import numpy as np
import os
from envirophat import weather #sudo apt-get install python3-envirophat
import Adafruit_DHT #sudo pip3 install Adafruit_DHT
import RPi.GPIO as GPIO

"""Temperature_sensor = degree celsiue
Pressure_sensor = hPa(mbar)
Latitude = decimal
station_height = meters"""

index_rh = 45 #If Humidity is below than this value, pump will be started.
logfile = '/home/pi/run_pump/log/'
Latitude=10.72
station_height=13.657

GPIO.setmode(GPIO.BCM) # set up BCM GPIO numbering


# Setup GPIO
pin_pump = 27
pin_switch = 22
pin_dht = 21
GPIO.setup(pin_pump, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(pin_switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# DHT22
sensor = Adafruit_DHT.DHT22

if not os.path.exists('/home/pi/run_pump/log/'):
    os.makedirs('/home/pi/run_pump/log/')

# Setup pressure correction
class CorrectPressure:
    
    def __init__(self, Temperature_sensor, Pressure_sensor, Latitude, station_height):
        self.Temp = Temperature_sensor #Degree celsius
        self.P0 = Pressure_sensor #hPa from sensor
        self.Lat = Latitude# Decimal
        self.H = station_height #Meter
        
    def cal_qnh(self):
        lat_zeta = self.Lat*(np.pi/180) #Change Decimal to Radient
        a = 0.002637*np.cos(2*lat_zeta)
        b1 = ((np.cos(2*lat_zeta))+1)/2
        b = 0.0000059*(b1)
        ab = (9.80616/9.80665)*(1 - a + b)
        
        Cg = (ab-1)*self.P0 #Optimize gravity effect value
        
        Cgh = ((-3.147)*(np.power(0.1,7))*self.H)*self.P0 #Optimize station height value

        Pgh = self.P0 + (Cg + Cgh) #Corrected station pressure
        
        Tmsl = self.Temp/100 
        #Lapse rate 1 degree celsiue per 100 meters
        #Tmsl is temperature at mean sea level pressure
        
        Tm = (self.Temp+Tmsl)/2 #Tm is average temperature
        s1 = 1 + (0.00367*Tm)
        s = self.H/(7991.15*s1)
        Pdelta = (np.exp(s)-1)*Pgh
        
        Pmsl = (Pgh + Pdelta)/100
        
        return Pmsl

# Setup data logger
class Logger:
    def __init__(self, temperature, humidity, qnh, logfile):
        self.data_dict = {}
        self.temperature = temperature
        self.humidity = humidity
        self.qnh = qnh
        self.logfile = logfile

    def collect_data(self):
        ''' collect data and assign to class variable '''
        self.data_dict['sensor'] = (datetime.now(), self.temperature, self.humidity, self.qnh)
    
    def log_data(self, datestamp):
        ''' log the data into csv files '''
        for file, data in self.data_dict.items():
            with open(self.logfile + file + str(datestamp) + '.csv', 'a+', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(data)

# Setup lcd
lcd = lcddriver.lcd()
lcd.lcd_display_string("System is running", 1)
lcd.lcd_display_string("Temp: ", 2)
lcd.lcd_display_string("Rh: ", 3)
lcd.lcd_display_string("Pump status: Auto", 4)

# Setup toggle switch
def toggle_switch(pin_switch):
    if GPIO.input(pin_switch):
        lcd.lcd_display_string("Pump status: off", 4)
        time.sleep(3)
        GPIO.output(pin_pump, GPIO.LOW)
        lcd.lcd_display_string("Pump status: Auto", 4)
    else:
        lcd.lcd_display_string("Pump status: on", 4)
        time.sleep(3)
        GPIO.output(pin_pump, GPIO.HIGH)
 
# listen for changing edge on toggle switch (both directions)
# event will interrupt the program and call the toggleLine function
GPIO.add_event_detect(pin_switch, GPIO.BOTH, callback=toggle_switch, bouncetime=300)

try:
    
    lcd.lcd_display_string("Pump status: Auto", 4)
    
    while True:
        
        datestamp = datetime.now().date()
        time.sleep(2)
        
        #BMP280
        pressure280 = weather.pressure()
        temperature280 = weather.temperature()
        obj = CorrectPressure(Temperature_sensor=temperature280, Pressure_sensor=pressure280, Latitude=Latitude, station_height=station_height)
        qnh = obj.cal_qnh()
        time.sleep(3)

        #DHT22
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin_dht)
        
        #Data logger
        logger = Logger(temperature, humidity, qnh, logfile)
        logger.collect_data()
        logger.log_data(datestamp)
        
        if humidity is not None and temperature is not None:
            txt_temp = "Temp: {temperature:.2f}"
            txt_rh = "Rh: {humidity:.2f}"
            lcd.lcd_display_string(txt_temp.format(temperature=temperature), 2)
            lcd.lcd_display_string(txt_rh.format(humidity=humidity), 3)
            if humidity < index_rh:
                time.sleep(3)
                GPIO.output(pin_pump, GPIO.HIGH)
                time.sleep(180)
                GPIO.output(pin_pump, GPIO.LOW)
            time.sleep(10)
        
except KeyboardInterrupt:
    GPIO.cleanup()