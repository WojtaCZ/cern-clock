import decoder
import buzzer
import time
import configuration
import asyncio
import ntp
import accelerometer
import backlight
import machine
import logging
logger = logging.getLogger(__name__)


lastActivityTimestamp = 0

FIRST_SETUP = None
WELCOME_NAME = None

SLEEP_ENABLED = None
SLEEP_TIMEOUT = None
SLEEP_TIMERANGE = None
# Array with two integers expressing the time range in seconds from 00:00 
# 72000 = 20:00, 28800 = 8:00
SLEEP_TIMERANGE_ARRAY = [72000, 28800]

async def loadScreen():
    for i in range(8, 0, -1):
        await decoder.writeString(await decoder.sflr("O", i))
        await asyncio.sleep_ms(200)
    for i in range(1, 9, 1):
        await decoder.writeString(await decoder.sflr("O", i))
        await asyncio.sleep_ms(200)

def turnOnSequence():
    # Slow ramp up sound
    for i in range(50, 400, 1):
        buzzer.beep(i, 8)
    buzzer.beep(500, 400)

    # Quick "collision" sounds
    decoder.writeStringSync("  C     ")
    for i in range(3000, 1000, -40):
        buzzer.beep(i, 5)

    decoder.writeStringSync("  CE    ")
    for i in range(3000, 1000, -40):
        buzzer.beep(i, 5)

    decoder.writeStringSync("  CER   ")
    for i in range(3000, 1000, -40):
        buzzer.beep(i, 5)

    decoder.writeStringSync("  CERN  ")
    for i in range(3000, 1000, -40):
        buzzer.beep(i, 5)
    time.sleep_ms(200)

    # Quicker ramp up
    for i in range(50, 1000, 20):
        buzzer.beep(i, 8)
    buzzer.beep(i, 1000)
    time.sleep_ms(200)

    # Quick collisions again
    decoder.writeStringSync(" H      ")
    for i in range(3000, 1000, -40):
        buzzer.beep(i, 5)

    decoder.writeStringSync(" HO     ")
    for i in range(3000, 1000, -40):
        buzzer.beep(i, 5)

    decoder.writeStringSync(" HOD    ")
    for i in range(3000, 1000, -40):
        buzzer.beep(i, 5)

    decoder.writeStringSync(" HODI   ")
    for i in range(3000, 1000, -40):
        buzzer.beep(i, 5)
        
    decoder.writeStringSync(" HODIN  ")
    for i in range(3000, 1000, -40):
        buzzer.beep(i, 5)
        
    decoder.writeStringSync(" HODINY ")
    for i in range(3000, 1000, -40):
        buzzer.beep(i, 5)

    # A little delay
    time.sleep_ms(2000)

    # Clear the screen
    decoder.writeStringSync("        ")

    # Three beeps to indicate full turnon
    buzzer.beep(800, 500)
    buzzer.beep(1000, 500)
    buzzer.beep(1200, 500)

def firstSetupSequence():
    global WELCOME_NAME
    decoder.writeBannerSync("AHOJ " + WELCOME_NAME)
    decoder.writeBannerSync("TED TE PROVEDU MYM NASTAVENIM")
    decoder.writeBannerSync("REAGUJI NA DOTYK!")
    
    accelerometer.enable()
    accelerometer.overrideSleep = True
    
    while not accelerometer.tapFlag:
        decoder.writeBannerSync("KLEPNI NA ME", 1, True)

    accelerometer.tapFlag = False
    accelerometer.tapCounter = 0
    accelerometer.disable()
    accelerometer.overrideSleep = False
    
    buzzer.beepOK()
    decoder.writeStringSync(" SUPER! ")
    time.sleep_ms(2000)
    decoder.writeBannerSync("JEDNIM KLEPNUTIM PREPINAS MODY")
    
    accelerometer.enable()
    accelerometer.overrideSleep = True
    
    while accelerometer.tapCounter < 2:
        if accelerometer.tapCounter == 0: 
            decoder.writeBannerSync("KLEPNI DVAKRAT", 1, True)
        elif accelerometer.tapCounter == 1 and accelerometer.tapFlag:
            decoder.writeBannerSync("MUSIS RYCHLEJI ZA SEBOU")
            accelerometer.tapFlag = False
            accelerometer.tapCounter = 0
            buzzer.beepERR()
    
    accelerometer.tapFlag = False
    accelerometer.tapCounter = 0
    accelerometer.disable()
    accelerometer.overrideSleep = False

    buzzer.beepOK()
    backlight.fadeOn(1000)
    decoder.writeStringSync(" KRASA! ")
    time.sleep_ms(2000)
    decoder.writeBannerSync("DVE KLEPNUTI OVLADAJI PODSVICENI")
    
    decoder.writeStringSync(" HOTOVO ")
    buzzer.beep(800, 500)
    buzzer.beep(1000, 500)
    buzzer.beep(1200, 500)
    time.sleep_ms(2000)

    decoder.writeBannerSync("TED ZAPNU SVOU WIFI CERN-CLOCK")
    decoder.writeBannerSync("PRIPOJ SE A NASTAV ME")

    
def init():
    global SLEEP_ENABLED
    global SLEEP_TIMEOUT
    global SLEEP_TIMERANGE
    global SLEEP_TIMERANGE_ARRAY
    global FIRST_SETUP
    global WELCOME_NAME

    # See if the clock is set up for the first time
    FIRST_SETUP = configuration.read("first_setup")
    if FIRST_SETUP == None or FIRST_SETUP == "false":
        FIRST_SETUP = False
    elif FIRST_SETUP == "true":
        FIRST_SETUP = True
        configuration.update("first_setup", "false")
    
    # Get the name of the owner
    WELCOME_NAME = configuration.read("welcome_name")
    if WELCOME_NAME == None:
        WELCOME_NAME = "CLOVECE"

    # See if the sleep is enabled in the config
    SLEEP_ENABLED = configuration.read("screen_sleep_timeout_enable")
    if SLEEP_ENABLED == None or SLEEP_ENABLED == "false":
        SLEEP_ENABLED = False
        logger.warning("Sleep timeout set to disabled")
    elif SLEEP_ENABLED == "true":
        SLEEP_ENABLED = True

    # Get the sleep timeout (its i)
    SLEEP_TIMEOUT = configuration.read("screen_sleep_timeout_seconds")

    try:
        # Try to convert to integer (seconds)
        SLEEP_TIMEOUT = int(SLEEP_TIMEOUT)
    except:
        # If not successful, set to default
        SLEEP_TIMEOUT = 10
        logger.warning("Sleep timeout not specified, using 10s")
    
    # Get the timerange for the sleeping
    SLEEP_TIMERANGE = configuration.read("screen_sleep_timerange")
    if SLEEP_TIMERANGE == None:
        # If invalid, use the default
        logger.warning("Timerange not valid, leaving the default 20:00 - 8:00")
    else:
        try:
            # Try to split it and convert to integers
            split = SLEEP_TIMERANGE.replace("-", ":").split(":")
            SLEEP_TIMERANGE_ARRAY[0] = (int(split[0]) * 60 * 60) + int(split[1]) * 60
            SLEEP_TIMERANGE_ARRAY[1] = (int(split[2]) * 60 * 60) + int(split[3]) * 60

        except:
            SLEEP_TIMERANGE_ARRAY = [72000, 28800]
            logger.warning("Timerange not valid, leaving the default 20:00 - 8:00")

def wakeUp():
    global lastActivityTimestamp
    lastActivityTimestamp = time.mktime(ntp.localTime())

def shouldSleep(timeTuple):
    global lastActivityTimestamp
    global SLEEP_ENABLED
    global SLEEP_TIMEOUT
    global SLEEP_TIMERANGE_ARRAY
    year, month, mday, hour, minute, second, weekday, yearday = timeTuple
    
    # Never sleep if not enabled
    if not SLEEP_ENABLED:
        return False
    
    # Create timestamp from the provided time
    timestampNow = time.mktime((year, month, mday, hour, minute, second, weekday, yearday))
    secondOfTheDay = (timestampNow % 86400)
    
    # If the timeout has not passed yet
    if (lastActivityTimestamp + SLEEP_TIMEOUT) > timestampNow:
        return False
    
    # If the timeout from last 
    # Create a timestamp of the todays and tomorrows midnight
    #midnightToday = time.mktime((year, month, mday, 0, 0, 0, weekday, yearday))
    #midnightTomorrow = midnightToday + 86400
    
    
    # If the first time is bigger than the second, the timerange spans two days
    if SLEEP_TIMERANGE_ARRAY[0] > SLEEP_TIMERANGE_ARRAY[1]:
        # If the timestamp is between todays and tomorrows limit
        #if timestampNow > (midnightToday + SLEEP_TIMERANGE_ARRAY[0]) and timestampNow < (midnightTomorrow + SLEEP_TIMERANGE_ARRAY[1]):
        if secondOfTheDay > SLEEP_TIMERANGE_ARRAY[0] or secondOfTheDay < SLEEP_TIMERANGE_ARRAY[1]:
            return True
        else:
            return False
        
    # The timerange spans just one day 
    else:
        # If the timestamp now is between the lower and upper limit
        #if timestampNow > (midnightToday + SLEEP_TIMERANGE_ARRAY[0]) and timestampNow < (midnightToday + SLEEP_TIMERANGE_ARRAY[1]):
        if secondOfTheDay > SLEEP_TIMERANGE_ARRAY[0] and secondOfTheDay < SLEEP_TIMERANGE_ARRAY[1]:
            return True
        else:
            return False

# Restart the clock
def restart():
    if backlight.isLitSync():
        backlight.fadeOffSync()

    decoder.writeStringSync("RESETUJI")
    time.sleep_ms(2000)
    machine.reset()