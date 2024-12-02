import os
import logging
import io

import gc
import micropython
import requests

import _thread

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
import asyncio

import taphandler
import usocket
from machine import Timer

try:
    file=open("website/index.html","r");
except:
    raise Exception("Cannot load HTML file for the webserver.");

HTML = file.read();
file.close();

# Backlight & buzzer controls



BUZZER_PWM		 = machine.PWM(Pin(17));
BUZZER_PWM.freq(500);
BUZZER_PWM.duty_u16(0);
#BUZZER_PWM			 = Pin(17, Pin.OUT, value=1)


decoder.deassertReset();
wireless.init();
#ntp.init();
#ntp.sync();
accelerometer.init();

dd = None


class connect():
    def post(self, data):
        global dd
        """Add customer"""
        dd = data
        BUZZER_PWM.duty_u16(30000);
        time.sleep_ms(300);
        BUZZER_PWM.duty_u16(0);
        # Return message AND set HTTP response code to "201 Created"
        return {'message': data}, 201

app = tinyweb.webserver()
#app.add_resource(connect, '/connect')

@app.route('/')
async def index(request, response):
    await response.send_file("website/index.html")
    
@app.route('/style.css')
async def style(request, response):
    await response.send_file("website/style.css")    


#try:
    
#except:
    #print("oops")

#DECODER_RESETn.value(1);

#connect()
#set_time()
    
#Timer(period=100, mode=Timer.PERIODIC, callback=taphandler.screenHandler)¨
    

async def display_loop():
    counter = 0
    while True:
        string = await decoder.zfl(str(counter), 8);
        print(string)
        await decoder.writeString(string)
        

        #taphandler.screenHandler();
        await asyncio.sleep_ms(1000);
        counter += 1;
        
        #if accelerometer.tapFlag:
            #taphandler.tapHandler(accelerometer.tapCounter)
            #accelerometer.tapFlag = False;
            
app.loop.create_task(display_loop())            
app.run(host="0.0.0.0", port=80)

# Run the web server as the sole process



        




    
