import os
import logging
import io

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

import taphandler



try:
    file=open("index.html","r");
except:
    raise Exception("Cannot load HTML file for the webserver.");

HTML = file.read();
file.close();

# Backlight & buzzer controls
BACKLIGHT_PWM		 = Pin(16, Pin.OUT, value=1)



#BUZZER_PWM		 = machine.PWM(Pin(17));
#BUZZER_PWM.freq(500);
#BUZZER_PWM.duty_u16(50);
#BUZZER_PWM			 = Pin(17, Pin.OUT, value=1)




accelerometer.init();
wireless.init();

app = tinyweb.webserver()

@app.route('/')
async def index(request, response):
    # Start HTTP response with content-type text/html
    await response.start_html()
    # Send actual HTML page
    await response.send(HTML)
    

# Run the web server as the sole process
app.run(host="0.0.0.0", port=80)
#ntp.init();
#ntp.syncTime();
#try:
    
#except:
    #print("oops")

#DECODER_RESETn.value(1);

#connect()
#set_time()



while True:
    #if taptoggle == 0:
        #string_write(zfl(str(machine.RTC().datetime()[4]),2) + ":" + zfl(str(machine.RTC().datetime()[5]),2) + ":" + zfl(str(machine.RTC().datetime()[6]),2))
    #elif taptoggle == 1:
        #string_write(zfl(str(machine.RTC().datetime()[2]),2) + "." + zfl(str(machine.RTC().datetime()[1]),2) + "." + zfl(str(machine.RTC().datetime()[0])[2:4],2))
    if accelerometer.tapFlag:
        taphandler.taphandler(accelerometer.tapCounter)
        accelerometer.tapFlag = False;
        




    
