from machine import Pin
from machine import I2C
from machine import Timer
import time
import logging

import configuration

logger = logging.getLogger(__name__)

tapCounterInternal = 0
tapCounter = 0
tapFlag = False

# Accelerometer interface
ACCEL_CSn		 = Pin(22, Pin.OUT, value=1);
ACCEL_INT1		 = Pin(20, Pin.IN);
ACCEL_INT2		 = Pin(21, Pin.IN);
ACCEL_SDA		 = Pin(18, Pin.PULL_UP);
ACCEL_SCL		 = Pin(19, Pin.PULL_UP);
ACCEL_I2C = I2C(1, freq=100000, scl=ACCEL_SCL, sda=ACCEL_SDA);
ACCEL_I2C_ADD = 25;



def init():
    logger.debug("Initializing the accelerometer");
    
    if ACCEL_I2C.readfrom_mem(ACCEL_I2C_ADD, 0x0F, 1)[0] != 0x44:
        raise Exception("Wrong accelerometer ID!");
        return;
    
    logger.debug("Accelerometer detected. Setting up tap detection");
    
    # Set FS to 2g & enable lownoise
    ACCEL_I2C.writeto_mem(ACCEL_I2C_ADD, 0x25, b'\x04');
    # Tap detect routed to INT1
    ACCEL_I2C.writeto_mem(ACCEL_I2C_ADD, 0x23, b'\x40');
    
    # Tap tresholds & enabling
    tapEnableBits = 0; 
    tapEnabled = configuration.read("tap_enable_x");
    print(tapEnabled)
            
    if tapEnabled == "true":
        tapEnableBits |= 0x80;
        logger.debug("Tap detection on X axis enabled.");
        try:
            tapTreshold = int(configuration.read("tap_treshold_x"));

            if tapTreshold > 31 or tapTreshold < 0:
                logger.warning("Tap treshold for X axis is out of limits, it will be constrained to comply with the limits");
                tapTreshold = max(min(31, tapTreshold, 0));
            
            logger.debug("Setting tap treshold for X axis to " + str(tapTreshold));
            ACCEL_I2C.writeto_mem(ACCEL_I2C_ADD, 0x30, tapTreshold.to_bytes(1))
        except:
            logger.warning("Tap treshold for X axis has not been found, even though tap detection is enabled. Setting to treshold 6");
            ACCEL_I2C.writeto_mem(ACCEL_I2C_ADD, 0x30, b'\x06')
    else:
        logger.debug("Tap detection on X axis disabled");
    
    tapEnabled = configuration.read("tap_enable_y");
     
    if tapEnabled == "true":
        tapEnableBits |= 0x40;
        logger.debug("Tap detection on Y axis enabled");
        try:
            tapTreshold = int(configuration.read("tap_treshold_y"));
            
            if tapTreshold > 31 or tapTreshold < 0:
                logger.warning("Tap treshold for Y axis is out of limits, it will be constrained to comply with the limits");
                tapTreshold = max(min(31, tapTreshold, 0));
            
            logger.debug("Setting tap treshold for Y axis to " + str(tapTreshold));
            ACCEL_I2C.writeto_mem(ACCEL_I2C_ADD, 0x31, tapTreshold.to_bytes(1))
        except:
            logger.warning("Tap treshold for Y axis has not been found, even though tap detection is enabled. Setting to treshold 6");
            ACCEL_I2C.writeto_mem(ACCEL_I2C_ADD, 0x31, b'\x06')  
    else:
        logger.debug("Tap detection on Y axis disabled");
            
    tapEnabled = configuration.read("tap_enable_z");
    
    if tapEnabled == "true":
        tapEnableBits |= 0x20;
        logger.debug("Tap detection on Z axis enabled.");
        try:
            tapTreshold = int(configuration.read("tap_treshold_z"));
            
            if tapTreshold > 31 or tapTreshold < 0:
                logger.warning("Tap treshold for Z axis is out of limits, it will be constrained to comply with the limits");
                tapTreshold = max(min(31, tapTreshold, 0));
            
            logger.debug("Setting tap treshold for Z axis to " + str(tapTreshold));
            ACCEL_I2C.writeto_mem(ACCEL_I2C_ADD, 0x32, (tapTreshold | tapEnableBits).to_bytes(1))
        except:
            logger.warning("Tap treshold for Z axis has not been found, even though tap detection is enabled. Setting to treshold 6");
            ACCEL_I2C.writeto_mem(ACCEL_I2C_ADD, 0x32,  (6 | tapEnableBits).to_bytes(1))     
    else:
        logger.debug("Tap detection on Z axis disabled");
    
    # Set shock duration
    ACCEL_I2C.writeto_mem(ACCEL_I2C_ADD, 0x33, b'\x02');
    # Run mode @ 400Hz, high performance
    ACCEL_I2C.writeto_mem(ACCEL_I2C_ADD, 0x20, b'\x74');
    time.sleep(1)
    # Enable interrupts
    ACCEL_I2C.writeto_mem(ACCEL_I2C_ADD, 0x3F, b'\x20');

def recognizeTap(p):
    global tapCounterInternal
    global tapCounter
    global tapTimer
    global tapFlag
    
    tapTimer.deinit()
    tapCounter = tapCounterInternal;
    tapCounterInternal = 0;
    tapFlag = True;
        
    
def int1_handler(p):
    global tapTimer
    global tapCounterInternal
    if tapCounterInternal == 0:
        tapTimer = Timer(period=300, mode=Timer.ONE_SHOT, callback=recognizeTap)
    
    tapCounterInternal += 1;


# Register accel interrupt
ACCEL_INT1.irq(trigger=Pin.IRQ_RISING, handler=int1_handler);


