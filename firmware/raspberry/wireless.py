import network
import socket
import time
import struct
import configuration
import logging

logger = logging.getLogger(__name__)

WIFI_SSID = None
WIFI_PASSWORD = None
AP_SSID = None

ADAPTER = network.WLAN(network.STA_IF)
CONNECT_MAXWAIT_SEC = 20
AP_MAXWAIT_SEC = 20

def activateAP():
    global AP_SSID
    global ADAPTER
    global AP_MAXWAIT_SEC
    
    ADAPTER = network.WLAN(network.AP_IF)
    ADAPTER.config(essid=AP_SSID, security=0);
    ADAPTER.active(True);
        
    maxwait = AP_MAXWAIT_SEC
    while maxwait > 0:
        if ADAPTER.active():
            break
        maxwait -= 1
        logger.debug("Activating the AP with SSID '" + str(AP_SSID) + "'");
        time.sleep(1)
        
    if not ADAPTER.active():
        raise Exception('Failed to activate the AP')
    else: 
        logger.debug("AP mode is active");
    
def connect():
    global WIFI_SSID
    global WIFI_PASSWORD
    global ADAPTER
    global CONNECT_MAXWAIT_SEC
    
    ADAPTER.active(True)
    ADAPTER.connect(WIFI_SSID, WIFI_PASSWORD)
    
    maxwait = CONNECT_MAXWAIT_SEC
    while maxwait > 0:
        if ADAPTER.status() < 0 or ADAPTER.status() >= 3:
            break
        maxwait -= 1
        logger.debug("Connecting to SSID '" + str(WIFI_SSID) + "'.");
        time.sleep(1)

    if ADAPTER.status() != 3:
        raise Exception('Network connection failed')
    else:
        logger.debug("Connected to '" + str(WIFI_SSID) + "' with IP " + str(ADAPTER.ifconfig()[0]));

    

def disconnect():
    global ADAPTER
    
    ADAPTER.active(False)
    ADAPTER.disconnect()
        
def init():
    global AP_SSID
    global WIFI_SSID
    global WIFI_PASSWORD
    global ADAPTER
    
    WIFI_SSID = configuration.read("wifi_ssid");
    WIFI_PASSWORD = configuration.read("wifi_password");
        
    AP_SSID = configuration.read("ap_ssid");
    if AP_SSID == None:
        AP_SSID = "CERN CLOCK";
        logger.warning("AP SSID not specified, using the default 'CERN CLOCK'");
    
    if WIFI_SSID == None or WIFI_PASSWORD == None:
        logger.warning("WIFI credentials not specified, switching to AP mode");
        activateAP();
    else:
        try:
            logger.debug("Trying to connect to SSID '" + str(WIFI_SSID));
            connect();
        except:
            logger.warning("WIFI connection unsuccesfull, switching to AP mode");
            activateAP();