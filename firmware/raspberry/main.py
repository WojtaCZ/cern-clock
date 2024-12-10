from machine import Pin
from machine import Timer
import time
import decoder
import accelerometer
import ntp
import wireless
import web
import vistars
import asyncio
import backlight
import buzzer
import clock
import logging
logging.basicConfig(level=logging.DEBUG)

# Variables holding the actve screen ID and indicating screen change
activeScreen = 0
activeScreenOld = -1
activeScreenChanged = True

# Routines to handle returning to home screen after some time
homeTimerLastActivityTimestamp = 0
homeTimerActive = True
HOME_TIMEOUT = 5000

def homeTimerStart():
    global homeTimerLastActivityTimestamp, homeTimerActive, HOME_TIMEOUT

    homeTimerLastActivityTimestamp = time.ticks_ms()
    homeTimerActive = True

def homeTimerStop():
    global homeTimerLastActivityTimestamp, homeTimerActive, HOME_TIMEOUT

    homeTimerActive = False

async def homeTimerProcess():
    global homeTimerLastActivityTimestamp, homeTimerActive, HOME_TIMEOUT
    global activeScreen

    if time.ticks_ms() > (homeTimerLastActivityTimestamp + HOME_TIMEOUT) and homeTimerActive:
        homeTimerStop()
        activeScreen = 0

# Routines to handle periodic NTP syncs
syncHourOld = -1
ntpErrors = 0

async def ntpSyncProcess(timeTuple):
    global syncHourOld, ntpErrors
    
    year, month, mday, hour, minute, second, weekday, yearday = timeTuple
    
    # If the hour has changed from the last one
    if hour != syncHourOld:
        # Try to sync the NTP
        try:
            ntp.sync()
            syncHourOld = hour
            ntpErrors = 0

        # If it failed, increase error counter
        except:
            ntpErrors += 1
                
        # If we were not able to sync for the full day, restart...
        if ntpErrors >= 24:
            clock.restart()


async def displayLoop():
    global activeScreen, activeScreenOld, activeScreenChanged
    global homeTimerLastActivityTimestamp, homeTimerActive, HOME_TIMEOUT

    global syncHourOld
    global ntpErrors
    
    # Set the last activity to be now so the clock doesnt sleep right away
    clock.wakeUp()
    
    while True:
        
        # Get the time
        timeNow = ntp.localTime()

        # Check if the time has passed to go to the home screen
        await homeTimerProcess()

        # See if there is need to sync the NTP
        await ntpSyncProcess(timeNow)

        # Check if the active screen changed or there was a tap
        if activeScreen != activeScreenOld:
            # If so, render the new screen
            activeScreenChanged = True
            activeScreenOld = activeScreen
        
        # If the clock shall not sleep, draw the selected screen
        if not clock.shouldSleep(timeNow):
            # Show the time
            if activeScreen == 0:
                hour = await decoder.zfl(str(timeNow[3]), 2)
                minute = await decoder.zfl(str(timeNow[4]), 2)
                second = await decoder.zfl(str(timeNow[5]), 2)

                await decoder.writeString(hour + ":" + minute + ":" + second)
                
            # Show the date
            elif activeScreen == 1:
                if activeScreenChanged:
                    # Start the home timer
                    homeTimerStart()
                
                day = await decoder.zfl(str(timeNow[2]), 2)
                month = await decoder.zfl(str(timeNow[1]), 2)
                year = str(timeNow[0])[2:4]

                await decoder.writeString(day + "." + month + "." + year)

            # Request the data from the vistars OCR
            elif activeScreen == 2:
                if activeScreenChanged:
                    # Stop the home timer
                    homeTimerStop()
                    
                accelerometer.disable()
                await decoder.writeString("STAV LHC")
                await vistars.getData()

                # After the request finished, show the data
                activeScreen = 3
            # Show the vistars data
            elif activeScreen == 3 and vistars.status != None:
                if activeScreenChanged:
                    homeTimerStart()
                
                # Show the retrieved data
                await decoder.writeString(vistars.status)
                
                accelerometer.enable()

            activeScreenChanged = False

        # If the clock should sleep
        else:
            # Go to home screen and blank the display
            activeScreen = 0
            await decoder.writeString("        ")
            
        # If the accel was tapped
        if accelerometer.tapFlag:  
            # If only once, go to next screen
            if accelerometer.tapCounter == 1:
                activeScreen += 1

            # If more than once, toggle the backlight
            else:
                if await backlight.isLit():
                    await backlight.fadeOff(1000)
                else:
                    await backlight.fadeOn(1000)

            # Clear the flag
            accelerometer.tapFlag = False
                
        # The max number of screens is 4, loop back to 0
        if activeScreen == 4:
            activeScreen = 0
                
        # Sleep for a little
        await asyncio.sleep_ms(50)

# If the wifi doesnt connect, this loop runs forever to notify the user
async def apLoop():
    while True:
        await decoder.writeBanner("PRIPOJ SE K MEMU AP NA ADRESU " + wireless.ADAPTER.ifconfig()[0] + " A NASTAV MI WIFI")

# Enable the decoder
decoder.deassertReset()

# Load system related config (sleep time)
clock.init()

# Load vistars configuration
vistars.init()

# Play the turnon animation
clock.turnOnSequence()

# Init the accelerometer
try:       
    accelerometer.init()

# If it failed, thats fatal...
except:
    buzzer.beepERR()
    while True:
        decoder.writeBannerSync("FATALNI CHYBA! NELZE NASTAVIT AKCELEROMETR")

# If the clock has not been setup yet, run through the first setup
if clock.FIRST_SETUP:
    clock.firstSetupSequence()

# Try to init the wireless 
try:
    wireless.init()

# If it fails, thats fatal... Loop forever
except:
    buzzer.beepERR()
    while True:
        decoder.writeBannerSync("FATALNI CHYBA! NELZE AKTIVOVAT WIFI ANI AP")
        
# If the wireless was initialized but in the AP mode (not able to connect to wifi)
if wireless.apActive:
    # Run the AP loop together with the WEB interface to allow for configuration
    web.app.loop.create_task(apLoop())
    web.app.run(host="0.0.0.0", port=80)

# Sync the NTP
try:
    decoder.writeStringSync("ZISKAVAM")
    time.sleep_ms(1000)
    decoder.writeStringSync(" PRESNE ")
    time.sleep_ms(1000)
    decoder.writeStringSync(" HODINY ")
    time.sleep_ms(1000)
    
    ntp.init()
    ntp.sync()

# If it failed, thats fatal...
except:
    buzzer.beepERR()
    while True:
        decoder.writeBannerSync("FATALNI CHYBA! NELZE SYNCHRONIZOVAT NTP")

accelerometer.enable()

# If all went well, register the display loop as an async task to run alongside the webserver
web.app.loop.create_task(displayLoop()) 
# Run the main app  
web.app.run(host="0.0.0.0", port=80)



        




    

