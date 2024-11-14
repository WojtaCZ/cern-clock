import network
import socket
import time
import struct
import configuration
import logging

logger = logging.getLogger(__name__)

NTP_DELTA = 2208988800
NTP_SERVER = None
NTP_TIMEZONE = None


def init():
    NTP_SERVER = configuration.read("ntp_server");
    if NTP_SERVER == None:
        raise Exception("NTP server not specified!");
        
    NTP_TIMEZONE = configuration.read("ntp_timezone");
    if NTP_TIMEZONE == None:
        NTP_TIMEZONE = 0;
        logger.warning("Timezone not specified, using 0");
    else:
        try:
            NTP_TIMEZONE = int(NTP_TIMEZONE);
        except:
            NTP_TIMEZONE = 0;
            logger.warning("Failed to convert timezone to number, using the default 0");
            
def syncTime():
    logger.debug("Syncing the local time to the NTP server");
    try:
        NTP_QUERY = bytearray(48)
        NTP_QUERY[0] = 0x1B
        addr = socket.getaddrinfo(host, 123)[0][-1]
        print(addr)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        try:
            s.settimeout(1)
            res = s.sendto(NTP_QUERY, addr)
            msg = s.recv(48)
        finally:
            s.close()
            
        val = struct.unpack("!I", msg[40:44])[0]
        t = val - NTP_DELTA    
        tm = time.gmtime(t)
        machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6], tm[3] + 1, tm[4], tm[5], 0))
    except:
        raise Exception("Unable to sync to the NTP server!");

    