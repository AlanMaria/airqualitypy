import os
import glob
import time
import httplib, urllib
#-----
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
SPICLK = 11
SPIMISO = 9
SPIMOSI = 10
SPICS = 8
mq7_apin = 0
mq7_dpin = 26
mq2_apin= 1
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)
GPIO.setup(mq7_dpin,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setwarnings(False)
GPIO.cleanup()	
	
# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler

#-----

sleep = 6 # how many seconds to sleep between posts to the channel
key = 'YP1E1PV7DW8VWT5B'# Thingspeak channel to update
#-----

GPIO.setwarnings(False)
GPIO.cleanup()			#clean up at the end of your script
GPIO.setmode(GPIO.BCM)		#to specify whilch pin numbering system
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)
GPIO.setup(mq7_dpin,GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
          
#read SPI data from MCP3008(or MCP3204) chip,8 possible adc's (0 thru 7)
def readadc(mq7_apin, SPICLK, SPIMOSI, SPIMISO, SPICS):#q7_apin, SPICLK, SPIMOSI, SPIMISO, SPICS)
        if ((mq7_apin > 7) or (mq7_apin < 0)):#Acnum, clockpin, mosipin, misopin, cspin
                return -1
        GPIO.output(SPICS, True)	
        GPIO.output(SPICLK, False)  # start clock low
        GPIO.output(SPICS, False)     # bring CS low
        commandout = mq7_apin
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(SPIMOSI, True)
                else:
                        GPIO.output(SPIMOSI, False)
                commandout <<= 1
                GPIO.output(SPICLK, True)
                GPIO.output(SPICLK, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(SPICLK, True)
                GPIO.output(SPICLK, False)
                mq7_apin  <<= 1
                if (GPIO.input(SPIMISO)):
                        mq7_apin  |= 0x1

        GPIO.output(SPICS, True)
        
        mq7_apin  >>= 1       # first bit is 'null' so drop it
        return mq7_apin 
#----- 
def readadcmq(mq2_apin, SPICLK, SPIMOSI, SPIMISO, SPICS):#q7_apin, SPICLK, SPIMOSI, SPIMISO, SPICS)
        if ((mq2_apin > 7) or (mq2_apin < 1)):#Acnum, clockpin, mosipin, misopin, cspin
                return -1
        GPIO.output(SPICS, True)	
        GPIO.output(SPICLK, False)  # start clock low
        GPIO.output(SPICS, False)     # bring CS low
        commandout = mq2_apin
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(SPIMOSI, True)
                else:
                        GPIO.output(SPIMOSI, False)
                commandout <<= 1
                GPIO.output(SPICLK, True)
                GPIO.output(SPICLK, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(SPICLK, True)
                GPIO.output(SPICLK, False)
                mq2_apin  <<= 1
                if (GPIO.input(SPIMISO)):
                        mq2_apin  |= 0x1

        GPIO.output(SPICS, True)
        
        mq2_apin  >>= 1       # first bit is 'null' so drop it
        return mq2_apin 
#---
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'
 
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
       
        return temp_c
 #-----


 #-----
def thermometer():
    while True:
        #Calculate temperature from sensor in Degrees C
        print "IoT Based Indoor Air Pollution Monitoring System"
        temp=read_temp();       
        print "Room Temperature in Degrees=",temp 
        print"please wait..."
        time.sleep(20)
        COlevel=readadc(mq7_apin, SPICLK, SPIMOSI, SPIMISO, SPICS)
        #print("CO level in current air")
        
        print"Current CO AD vaule = " +str("%.2f"%((COlevel/1024.)*5))+" V"
        print"Current CO density is:" +str("%.2f"%((COlevel/1024.)*100))+" %" 
        time.sleep(0.5) 
        print "CO in PPM=",COlevel/9.8; 
        
        smoke=readadcmq(mq2_apin, SPICLK, SPIMOSI, SPIMISO, SPICS)
        #print("smoke level in current air")
        print"Current CO AD vaule = " +str("%.2f"%((COlevel/1024.)*5))+" V"
        print"Current CO density is:" +str("%.2f"%((COlevel/1024.)*100))+" %" 
        time.sleep(0.5) 
        print "smoke level=",smoke;
        
                    
 
        params = urllib.urlencode({'field1': temp, 'key':key ,'field2': COlevel, 'key':key,'field3': smoke, 'key':key }) 
        headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
        conn = httplib.HTTPConnection("api.thingspeak.com:80")
        try:
            conn.request("POST", "/update", params, headers)
            response = conn.getresponse()
           
            print (response.status, response.reason)
            data = response.read()
            conn.close()
        except:
            print ("connection failed")
        break


if __name__ == "__main__":
        while True:
                thermometer()
                time.sleep(sleep)
