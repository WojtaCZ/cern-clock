from machine import Pin
from machine import I2C
from machine import Timer
import time
import buzzer
import clock
import configuration
import ntp
import logging
logger = logging.getLogger(__name__)

tapCounterInternal = 0
tapCounter = 0
tapFlag = False

# Accelerometer interface
ACCEL_CSn		 = Pin(22, Pin.OUT, value=1)
ACCEL_INT1		 = Pin(20, Pin.IN)
ACCEL_INT2		 = Pin(21, Pin.IN)
ACCEL_SDA		 = Pin(18, Pin.PULL_UP)
ACCEL_SCL		 = Pin(19, Pin.PULL_UP)
ACCEL_I2C = I2C(1, freq=100000, scl=ACCEL_SCL, sda=ACCEL_SDA)
ACCEL_I2C_ADD = 25

overrideSleep = False

# Handle the finished tap procedure
def tapHandler(p):
    global tapCounterInternal, tapCounter, tapTimer, tapFlag
    
    # Kill the timer
    tapTimer.deinit()
    
    # Update the vars
    tapCounter = tapCounterInternal
    tapCounterInternal = 0

    # Signal a finished tap for processing
    tapFlag = True
        
# If the tap interrupt was received
def int1_handler(p):
    global tapTimer, tapCounterInternal, overrideSleep
    
    # Beep
    buzzer.beep(600, 50)
    
    # Increase the tap count
    tapCounterInternal += 1

    # If the clock is not sleeping, behave ike a screen change
    timeNow = ntp.localTime()

    if (not clock.shouldSleep(timeNow)) or overrideSleep:
        # If it is the first tap, start a timer to wait for the possible second tap
        if tapCounterInternal == 1:
            tapTimer = Timer(period=600, mode=Timer.ONE_SHOT, callback=tapHandler)
        else:
            # Kill the timer and handle the taps
            tapTimer.deinit()
            tapHandler(0)

    # But if it is sleeping, wake it up
    else:
        clock.wakeUp()
        return
    
# Set up the accel
def init():
    logger.debug("Initializing the accelerometer")
    
    if ACCEL_I2C.readfrom_mem(ACCEL_I2C_ADD, 0x0F, 1)[0] != 0x44:
        raise Exception("Wrong accelerometer ID!")
    
    logger.debug("Accelerometer detected. Setting up tap detection")
    
    # Set FS to 2g & enable lownoise
    ACCEL_I2C.writeto_mem(ACCEL_I2C_ADD, 0x25, b'\x04')
    # Tap detect routed to INT1
    ACCEL_I2C.writeto_mem(ACCEL_I2C_ADD, 0x23, b'\x40')
    
    # Tap tresholds & enabling
    tapEnableBits = 0; 
    tapEnabled = configuration.read("tap_enable_x");
    print(tapEnabled)
            
    if tapEnabled == "true":
        tapEnableBits |= 0x80
        logger.debug("Tap detection on X axis enabled.")
        try:
            tapTreshold = int(configuration.read("tap_treshold_x"))

            if tapTreshold > 31 or tapTreshold < 0:
                logger.warning("Tap treshold for X axis is out of limits, it will be constrained to comply with the limits")
                tapTreshold = max(min(31, tapTreshold, 0))
            
            logger.debug("Setting tap treshold for X axis to " + str(tapTreshold))
            ACCEL_I2C.writeto_mem(ACCEL_I2C_ADD, 0x30, tapTreshold.to_bytes(1))
        except:
            logger.warning("Tap treshold for X axis has not been found, even though tap detection is enabled. Setting to treshold 6")
            ACCEL_I2C.writeto_mem(ACCEL_I2C_ADD, 0x30, b'\x06')
    else:
        logger.debug("Tap detection on X axis disabled")
    
    tapEnabled = configuration.read("tap_enable_y")
     
    if tapEnabled == "true":
        tapEnableBits |= 0x40
        logger.debug("Tap detection on Y axis enabled")
        try:
            tapTreshold = int(configuration.read("tap_treshold_y"))
            
            if tapTreshold > 31 or tapTreshold < 0:
                logger.warning("Tap treshold for Y axis is out of limits, it will be constrained to comply with the limits")
                tapTreshold = max(min(31, tapTreshold, 0))
            
            logger.debug("Setting tap treshold for Y axis to " + str(tapTreshold))
            ACCEL_I2C.writeto_mem(ACCEL_I2C_ADD, 0x31, tapTreshold.to_bytes(1))
        except:
            logger.warning("Tap treshold for Y axis has not been found, even though tap detection is enabled. Setting to treshold 6")
            ACCEL_I2C.writeto_mem(ACCEL_I2C_ADD, 0x31, b'\x06')  
    else:
        logger.debug("Tap detection on Y axis disabled")
            
    tapEnabled = configuration.read("tap_enable_z")
    
    if tapEnabled == "true":
        tapEnableBits |= 0x20
        logger.debug("Tap detection on Z axis enabled.")
        try:
            tapTreshold = int(configuration.read("tap_treshold_z"))
            
            if tapTreshold > 31 or tapTreshold < 0:
                logger.warning("Tap treshold for Z axis is out of limits, it will be constrained to comply with the limits")
                tapTreshold = max(min(31, tapTreshold, 0))
            
            logger.debug("Setting tap treshold for Z axis to " + str(tapTreshold))
            ACCEL_I2C.writeto_mem(ACCEL_I2C_ADD, 0x32, (tapTreshold | tapEnableBits).to_bytes(1))
        except:
            logger.warning("Tap treshold for Z axis has not been found, even though tap detection is enabled. Setting to treshold 6")
            ACCEL_I2C.writeto_mem(ACCEL_I2C_ADD, 0x32,  (6 | tapEnableBits).to_bytes(1))     
    else:
        ACCEL_I2C.writeto_mem(ACCEL_I2C_ADD, 0x32,  tapEnableBits.to_bytes(1))
        logger.debug("Tap detection on Z axis disabled")
    
    # Set shock duration
    ACCEL_I2C.writeto_mem(ACCEL_I2C_ADD, 0x33, b'\x02')
    # Run mode @ 400Hz, high performance
    ACCEL_I2C.writeto_mem(ACCEL_I2C_ADD, 0x20, b'\x74')
    time.sleep(1)
    # Enable interrupts
    ACCEL_I2C.writeto_mem(ACCEL_I2C_ADD, 0x3F, b'\x20')
    
def enable():
    # Register accel interrupt
    ACCEL_INT1.irq(trigger=Pin.IRQ_RISING, handler=int1_handler)

def disable():
    # Unregister accel interrupt
    ACCEL_INT1.irq(trigger=Pin.IRQ_RISING, handler=None)






