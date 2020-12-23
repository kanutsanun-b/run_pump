import lcddriver
#from time import *
import time
from envirophat import weather #sudo apt-get install python3-envirophat
import sys
import Adafruit_DHT #sudo pip3 install Adafruit_DHT
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM) # set up BCM GPIO numbering

#Setup GPIO
pin_pump = 21
pin_switch = 22
pin_dht = 20
channel_list =[pin_pump, pin_switch, pin_dht]
GPIO.setup(pin_pump, GPIO.OUT)
GPIO.setup(pin_switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#BMP280
ADDR=0x77
temp280 = weather.temperature()
pres280 = weather.pressure()

lcd = lcddriver.lcd()
lcd.lcd_display_string("System is running", 1)
lcd.lcd_display_string("Temp: ", 2)
lcd.lcd_display_string("Rh: ", 3)
lcd.lcd_display_string("Pump status: ", 4)

def toggle_switch(channel):
    if GPIO.input(pin_switch):
        GPIO.output(pin_pump, GPIO.HIGH)  # Turn motor on
    else:
        lcd.lcd_display_string("Pump status: off", 4)
        GPIO.output(pin_pump, GPIO.LOW)  # Turn motor off
        GPIO.cleanup()

#DHT22
sensor = Adafruit_DHT.DHT22
#while True:
#  humidity, temperature = Adafruit_DHT.read_retry(sensor, pin_dht)
#  if humidity is not None and temperature is not None:
#    print ('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
#    time.sleep(10)
#  else:
#    print ('Failed to get reading. Try again!')
    
# listen for changing edge on toggle switch (both directions)
# event will interrupt the program and call the toggleLine function
GPIO.add_event_detect(pin_switch, GPIO.BOTH, callback=toggle_switch, bouncetime=300)
    
if __name__ == '__main__':
    try:
        while True:
            humidity, temperature = Adafruit_DHT.read_retry(sensor, pin_dht)
            if humidity is not None and temperature is not None:
                #str_temp = print('Temp: {}'.format(temperature))
                #str_rh = print('Rh: ={}'.format(humidity))
                str_temp = str(temperature)
                str_rh = str(humidity)
                lcd.lcd_display_string(str_temp, 2)
                lcd.lcd_display_string(str_rh, 3)
                time.sleep(10)
            else:
                pass
    
    except KeyboardInterrupt:
        GPIO.cleanup()