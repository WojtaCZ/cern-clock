import network
import socket
import time
import struct
import configuration
import logging
import asyncio
import decoder
import buzzer

logger = logging.getLogger(__name__)

WIFI_SSID = None
WIFI_PASSWORD = None
AP_SSID = None

ADAPTER = network.WLAN(network.STA_IF)
CONNECT_MAXWAIT_SEC = 20
AP_MAXWAIT_SEC = 20

apActive = False
connActive = False

def activateAP():
    global AP_SSID
    global ADAPTER
    global AP_MAXWAIT_SEC
    global apActive
    
    ADAPTER = network.WLAN(network.AP_IF)
    ADAPTER.config(essid=AP_SSID, security=0);
    ADAPTER.active(True);
        
    maxwait = AP_MAXWAIT_SEC
    while maxwait > 0:
        if ADAPTER.active():
            break
        maxwait -= 1
        asyncio.run(decoder.writeString("AKTIVUJI"));
        time.sleep_ms(1000)
        asyncio.run(decoder.writeString("   AP   "));
        time.sleep_ms(1000)
        logger.debug("Activating the AP with SSID '" + str(AP_SSID) + "'");
        
        
    if not ADAPTER.active():
        asyncio.run(decoder.writeString(" CHYBA! "));
        time.sleep_ms(3000);
        apActive = False
        raise Exception('Failed to activate the AP')
    else: 
        logger.debug("AP mode is active");
        apActive = True

def wait_for(fun, timeout):
    start = time.time()
    while not fun():
        if time.time() - start > timeout:
            raise TimeoutError()
        time.sleep(0.1)

def disconnect():
    global ADAPTER
    
    ADAPTER.active(False)
    ADAPTER.disconnect()
    wait_for(lambda: not ADAPTER.isconnected(), 5)
    
def connect():
    global WIFI_SSID
    global WIFI_PASSWORD
    global ADAPTER
    global CONNECT_MAXWAIT_SEC
    global connActive
    
    ADAPTER.active(True)
    disconnect();
    ADAPTER.connect(WIFI_SSID, WIFI_PASSWORD)
  
    maxwait = CONNECT_MAXWAIT_SEC
    while maxwait > 0:
        if ADAPTER.status() < 0 or ADAPTER.status() >= 3:
            break
        maxwait -= 1
        asyncio.run(decoder.writeString("AKTIVUJI"));
        time.sleep_ms(1000)
        asyncio.run(decoder.writeString("  WIFI  "));
        time.sleep_ms(1000)
        logger.debug("Connecting to SSID '" + str(WIFI_SSID) + "'.");

    if ADAPTER.status() != 3:
        asyncio.run(decoder.writeString(" CHYBA! "));
        time.sleep_ms(3000);
        connActive = False
        raise Exception('Network connection failed')
    else:
        logger.debug("Connected to '" + str(WIFI_SSID) + "' with IP " + str(ADAPTER.ifconfig()[0]));
        asyncio.run(decoder.writeString("PRIPOJEN"));
        connActive = True
        buzzer.beepOK()
        time.sleep_ms(1500);
        asyncio.run(decoder.writeBanner("IP: " + str(ADAPTER.ifconfig()[0]), 1));

    
        
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