import lcddriver
import time
from envirophat import weather #sudo apt-get install python3-envirophat
import Adafruit_DHT #sudo pip3 install Adafruit_DHT
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM) # set up BCM GPIO numbering

#Setup GPIO
pin_pump = 21
pin_switch = 22
pin_dht = 20
GPIO.setup(pin_pump, GPIO.OUT)
GPIO.setup(pin_switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#DHT22
sensor = Adafruit_DHT.DHT22

lcd = lcddriver.lcd()
lcd.lcd_display_string("System is running", 1)
lcd.lcd_display_string("Temp: ", 2)
lcd.lcd_display_string("Rh: ", 3)
lcd.lcd_display_string("Pump status: ", 4)

def toggle_switch(pin_switch):
    if GPIO.input(pin_switch):
        GPIO.output(pin_pump, GPIO.HIGH)  # Turn motor on
    else:
        lcd.lcd_display_string("Pump status: off", 4)
        GPIO.output(pin_pump, GPIO.LOW)  # Turn motor off
 
# listen for changing edge on toggle switch (both directions)
# event will interrupt the program and call the toggleLine function
GPIO.add_event_detect(pin_switch, GPIO.BOTH, callback=toggle_switch, bouncetime=300)

try:
    while True:
        
        #BMP280
        temp280 = weather.temperature()
        pres280 = weather.pressure()
        
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin_dht)
        if humidity is not None and temperature is not None:
            txt_temp = "Temp: {temperature:.2f}"
            txt_rh = "Rh: {humidity:.2f}"
            lcd.lcd_display_string(txt_temp.format(temperature=temperature), 2)
            lcd.lcd_display_string(txt.rh.format(humidity=humidity), 3)
            time.sleep(10)
        else:
            print ('Failed to get reading. Try again!')
            
except KeyboardInterrupt:
    GPIO.cleanup()