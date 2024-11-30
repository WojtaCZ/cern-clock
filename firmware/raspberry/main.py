import os
import logging
import io

import gc
import micropython
import requests

logging.basicConfig(level=logging.DEBUG)

import time

from machine import Pin

#import wireless
import decoder
import accelerometer
import configuration
import ntp
import wireless
import tinyweb
import vistars

import taphandler
import usocket
from machine import Timer

#try:
    #file=open("index.html","r");
#except:
    #raise Exception("Cannot load HTML file for the webserver.");

#HTML = file.read();
#file.close();

# Backlight & buzzer controls



#BUZZER_PWM		 = machine.PWM(Pin(17));
#BUZZER_PWM.freq(500);
#BUZZER_PWM.duty_u16(50);
#BUZZER_PWM			 = Pin(17, Pin.OUT, value=1)


decoder.deassertReset();
wireless.init();
ntp.init();
ntp.sync();
accelerometer.init();





#app = tinyweb.webserver()

#@app.route('/')
#async def index(request, response):
    # Start HTTP response with content-type text/html
    #await response.start_html()
    # Send actual HTML page
   # await response.send(HTML)
    


# Run the web server as the sole process
#app.run(host="0.0.0.0", port=80)



#try:
    
#except:
    #print("oops")

#DECODER_RESETn.value(1);

#connect()
#set_time()
    
#Timer(period=100, mode=Timer.PERIODIC, callback=taphandler.screenHandler)

while True:
    taphandler.screenHandler(1);
    if accelerometer.tapFlag:
        taphandler.tapHandler(accelerometer.tapCounter)
        accelerometer.tapFlag = False;
        


        




    
