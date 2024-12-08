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
import backlight
import buzzer
import taphandler
import usocket
import urequests
import sleep

from machine import Timer

activeScreen = 0;
activeScreenOld = -1;

homeTimer = 0
homeTimerActive = True

syncHourOld = -1
ntpErrors = 0;

def initSequence():
    for i in range(50, 400, 1):
        buzzer.beep(i, 8)
    buzzer.beep(500, 400)

    asyncio.run(decoder.writeString("  C     "));
    for i in range(3000, 1000, -40):
        buzzer.beep(i, 5)

    asyncio.run(decoder.writeString("  CE    "));
    for i in range(3000, 1000, -40):
        buzzer.beep(i, 5)

    asyncio.run(decoder.writeString("  CER   "));
    for i in range(3000, 1000, -40):
        buzzer.beep(i, 5)

    asyncio.run(decoder.writeString("  CERN  "));
    for i in range(3000, 1000, -40):
        buzzer.beep(i, 5)

    time.sleep_ms(200)
    for i in range(50, 1000, 20):
        buzzer.beep(i, 8)
    buzzer.beep(i, 1000)
    time.sleep_ms(200)

    asyncio.run(decoder.writeString(" H      "));
    for i in range(3000, 1000, -40):
        buzzer.beep(i, 5)

    asyncio.run(decoder.writeString(" HO     "));
    for i in range(3000, 1000, -40):
        buzzer.beep(i, 5)

    asyncio.run(decoder.writeString(" HOD    "));
    for i in range(3000, 1000, -40):
        buzzer.beep(i, 5)

    asyncio.run(decoder.writeString(" HODI   "));
    for i in range(3000, 1000, -40):
        buzzer.beep(i, 5)
        
    asyncio.run(decoder.writeString(" HODIN  "));
    for i in range(3000, 1000, -40):
        buzzer.beep(i, 5)
        
    asyncio.run(decoder.writeString(" HODINY "));
    for i in range(3000, 1000, -40):
        buzzer.beep(i, 5)

    time.sleep_ms(2000);

    asyncio.run(decoder.writeString("        "));
    buzzer.beep(800, 500)
    buzzer.beep(1000, 500)
    buzzer.beep(1200, 500)

    asyncio.run(backlight.fadeOn(3000))





app = tinyweb.webserver()

async def infoResponse(data):
    return """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link rel="stylesheet" href="style.css">
                <title>CERN CLOCK</title>
            </head>
            <body class="quicksand-light instructions" >
                <div class="content">
            """ + data + """
                </div>
                
            </body>
            </html>
            """

class params():
    def get(self, data):
        resp = {}
        for key in data:
            resp[key] = configuration.read(key)
            
        return resp

    def post(self, data):
        for key in data:
            configuration.write(key, data[key])
            
        resp = {}
        for key in data:
            resp[key] = configuration.read(key)
        return resp, 201

app.add_resource(params, "/parameters");

@app.route('/')
async def index(request, response):
    await response.send_file("website/index.html")

@app.route('/connect.html')
async def connect(request, response):
    await response.send_file("website/connect.html")

@app.route('/restart.html')
async def restart(request, response):
    await response.send_file("website/restart.html")
    buzzer.beepOK()
    machine.reset()

@app.route('/params.html')
async def params(request, response):
    await response.send_file("website/params.html")
    
@app.route('/style.css')
async def style(request, response):
    await response.send_file("website/style.css")    

@app.route('/setwifi', methods = ['POST'], max_body_size = 2048, save_headers = ["Content-Length","Content-Type"], allowed_access_control_headers = ["Content-Length","Content-Type"])
async def connect(request, response):
    data = await request.read_parse_form_data()
    try:
        ssid = data["ssid"]
        password = data["pass"]
        
        configuration.write("wifi_ssid", ssid);
        configuration.write("wifi_password", password);
        
        await response.start_html()
        
        await response.send(await infoResponse("""
            <span class="quicksand-bold">Připojuji k WiFi...</span><br>
            <span class="quicksand-medium">""" + ssid + """</span>
        """))
        
        buzzer.beepOK();
        await decoder.writeString("RESETUJI")
        machine.reset()
        
    except:
        await response.start_html()
        await response.send(await infoResponse("""
            <span class="quicksand-bold">Chybně zaslaná data!</span><br>
        """))
        buzzer.beepERR();
    
    
   



def homeCallback(p):
    global activeScreen
    activeScreen = 0
    
async def loadScreen():
    for i in range(8, 0, -1):
        await decoder.writeString(await decoder.sflr("O", i));
        await asyncio.sleep_ms(200)
    for i in range(1, 9, 1):
        await decoder.writeString(await decoder.sflr("O", i));
        await asyncio.sleep_ms(200)

async def displayLoop():
    global loadVistars
    global activeScreen
    global activeScreenOld
    global homeTimer, homeTimerActive
    global syncHourOld
    global ntpErrors
    vistarsThread = None
    
    

    sleep.timer = time.ticks_ms();
    
    while True:
        
        dateTime = await ntp.localTime();
        hour = await decoder.zfl(str(dateTime[3]), 2);
        minute = await decoder.zfl(str(dateTime[4]), 2);
        second = await decoder.zfl(str(dateTime[5]), 2);
        
        if sleep.inTimeRange(int(hour), int(minute)) and sleep.enabled:
            sleep.timerActive = True;
        else:
            sleep.timerActive = False;
        
        if not sleep.timerActive or (time.ticks_ms() < (sleep.timer + sleep.timeout) and sleep.timerActive):
                      
            day = await decoder.zfl(str(dateTime[2]), 2)
            month = await decoder.zfl(str(dateTime[1]), 2)
            year = str(dateTime[0])[2:4]
            
            # Show the time
            if activeScreen == 0:
                if activeScreen != activeScreenOld:
                    activeScreenOld = activeScreen;
                    
                await decoder.writeString(hour + ":" + minute + ":" + second);
                
            # Show the date
            elif activeScreen == 1:
                if activeScreen != activeScreenOld:
                    homeTimer = time.ticks_ms();
                    homeTimerActive = True
                    activeScreenOld = activeScreen;
                    
                await decoder.writeString(day + "." + month + "." + year);

            # Summon the request 
            elif activeScreen == 2:
                if activeScreen != activeScreenOld:
                    homeTimerActive = False
                    activeScreenOld = activeScreen;
                    
                await decoder.writeString("STAV LHC");
                await vistars.getData();
                activeScreen = 3;

            elif activeScreen == 3 and vistars.status != None:
                if activeScreen != activeScreenOld:
                    homeTimer = time.ticks_ms();
                    homeTimerActive = True
                    activeScreenOld = activeScreen;
                    
                await decoder.writeString(vistars.status);
        else:
            activeScreen = 0;
            await decoder.writeString("        ");
            
        if accelerometer.tapFlag:  
            if accelerometer.tapCounter == 1:
                activeScreen += 1;
            else:
                if backlight.active:
                    await backlight.fadeOff(1000);
                else:
                    await backlight.fadeOn(1000);
            accelerometer.tapFlag = False;
                
        if hour != syncHourOld:
            try:
                ntp.sync();
                syncHourOld = hour;
                ntpErrors = 0;
            except:
                ntpErrors += 1;
                await decoder.writeBanner("CHYBA SYNCHRONIZACE NTP")
                
        if ntpErrors > 10:
            machine.restart();
        
        if activeScreen == 4:
            activeScreen = 0;
                
        if time.ticks_ms() > (homeTimer + 5000) and homeTimerActive:
            activeScreen = 0;
            homeTimerActive = False;

        await asyncio.sleep_ms(50)
        


decoder.deassertReset();

vistars.init()
sleep.init()

async def apLoop():
    while True:
        await decoder.writeBanner("PRIPOJ SE K MEMU AP NA ADRESU " + wireless.ADAPTER.ifconfig()[0] + " A NASTAV MI WIFI");
        
try:
    wireless.init();
except:
    buzzer.beepERR();
    while True:
        asyncio.run(decoder.writeBanner("FATALNI CHYBA! NELZE AKTIVOVAT WIFI ANI AP"));
        
if wireless.apActive:
    app.loop.create_task(apLoop())
    app.run(host="0.0.0.0", port=80)


asyncio.run(decoder.writeString("ZISKAVAM"));
time.sleep_ms(1000);
asyncio.run(decoder.writeString(" PRESNE "));
time.sleep_ms(1000);
asyncio.run(decoder.writeString(" HODINY "));

try:
    ntp.init();
    asyncio.run(ntp.sync());
except:
    buzzer.beepERR();
    while True:
        asyncio.run(decoder.writeBanner("FATALNI CHYBA! NELZE SYNCHRONIZOVAT NTP"));

try:       
    accelerometer.init();
except:
    buzzer.beepERR();
    while True:
        asyncio.run(decoder.writeBanner("FATALNI CHYBA! NELZE NASTAVIT AKCELEROMETR"));

app.loop.create_task(displayLoop())   
app.run(host="0.0.0.0", port=80)
# Run the web server as the sole process



        




    

