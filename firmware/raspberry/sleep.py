import configuration
import logging
logger = logging.getLogger(__name__)

timer = 0
timerActive = True
timeout = None
enabled = None
timerange = None

timerangeTuple = [20, 00, 8, 00]

def init():
    global timeout
    global enabled
    global timerange
    global timerangeTuple
   
    timeout = int(configuration.read("screen_sleep_timeout_seconds")) * 1000;
    if timeout == None:
        timeout = 10000
        logger.warning("Sleep timeout not specified, using 10s");
    
    enabled = configuration.read("screen_sleep_timeout_enable");
    if enabled == None or enabled == "false":
        enabled = False
        logger.warning("Sleep timeout set to disabled");
    elif enabled == "true":
        enabled = True
        
    timerange = configuration.read("screen_sleep_timerange");
    if timerange == None:
        logger.warning("Timerange not valid, leaving the default 20:00 - 8:00");
    else:
        try:
            split = timerange.replace("-", ":").split(":");
            timerangeTuple[0] = int(split[0])
            timerangeTuple[1] = int(split[1])
            timerangeTuple[2] = int(split[2])
            timerangeTuple[3] = int(split[3])
        except:
            timerangeTuple = [20, 00, 8 ,00]
            logger.warning("Timerange not valid, leaving the default 20:00 - 8:00");
        
def inTimeRange(h, m):
    if h > timerangeTuple[0] and h < timerangeTuple[2]:
        return True
    
    if h == timerangeTuple[0]:
        if m >= timerangeTuple[1]:
            return True
        
    if h == timerangeTuple[2]:
        if m < timerangeTuple[3]:
            return True

    return False
    
    