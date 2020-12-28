import lcddriver
import time
import csv
from datetime import datetime
from pressure2qnh import CorrectPressure #sudo pip3 install pressure2qnh
from envirophat import weather #sudo apt-get install python3-envirophat
import Adafruit_DHT #sudo pip3 install Adafruit_DHT
import RPi.GPIO as GPIO

"""Temperature_sensor = degree celsiue
Pressure_sensor = hPa(mbar)
Latitude = decimal
station_height = meters"""

index_rh = 45 #If Humidity is below than this value, pump will be started.
logfile = 'C:/Users/kanut/OneDrive/Documents_KB/python/RaspiZero_project/testlog/'
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

# Setup data logger
class Logger:
    def __init__(self, temperature, humidity, qnh):
        self.data_dict = {}
        self.temperature = temperature
        self.humidity = humidity
        self.qnh = qnh

    def collect_data(self):
        ''' collect data and assign to class variable '''
        self.data_dict['sensor'] = (datetime.now(), self.temperature, self.humidity, self.qnh)
    
    @staticmethod
    def log_data(logfile, datestamp):
        ''' log the data into csv files '''
        for file, data in Logger.data_dict.items():
            with open(logfile + file + str(datestamp) + '.csv', 'a+', newline='') as f:
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
        logger = Logger(temperature, humidity, qnh)
        logger.collect_data()
        logger.log_data(logfile, datestamp)
        
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
        
except:
    GPIO.cleanup()
        
