from time import gmtime, mktime
import configuration
import logging
import ntptime
import machine

logger = logging.getLogger(__name__)

NTP_SERVER = None
NTP_TIMEZONE = None


def init():
    global NTP_SERVER
    
    NTP_SERVER = configuration.read("ntp_server")
    if NTP_SERVER == None:
        raise Exception("NTP server not specified!")
        
    ntptime.timeout = 10
    ntptime.host = NTP_SERVER
    
async def sync():
    t = ntptime.time()
    tm = gmtime(t)
    machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))


async def localTime(secs: int | None = None) -> tuple[int, int, int, int, int, int, int, int]:
    """
    Implements daylight savings
    from: the last Sunday in March (02:00 CET)
    to:   the last Sunday in October (03:00 CEST)
    """

    def last_sunday(year: int, month: int, hour: int, minute: int) -> int:
        """Get the time of the last sunday of the month
        It returns an integer which is the number of seconds since Jan 1, 2000, just like mktime().
        """

        # Get the UTC time of the last day of the month
        seconds = mktime((year, month + 1, 0, hour, minute, 0, None, None))

        # Calculate the offset to the last sunday of the month
        (year, month, mday, hour, minute, second, weekday, yearday) = gmtime(seconds)
        offset = (weekday + 1) % 7

        # Return the time of the last sunday of the month
        return mktime((year, month, mday - offset, hour, minute, second, None, None))

    utc = gmtime(secs)

    # Find start date for daylight saving, i.e. last Sunday in March (01:00 UTC)
    start_secs = last_sunday(year=utc[0], month=3, hour=1, minute=0)

    # Find stop date for daylight saving, i.e. last Sunday in October (01:00 UTC)
    stop_secs = last_sunday(year=utc[0], month=10, hour=1, minute=0)

    utc_secs = mktime(utc)
    if utc_secs >= start_secs and utc_secs < stop_secs:
        delta_secs = 2 * 60 * 60  # Summer time (CEST or UTC + 2h)
    else:
        delta_secs = 1 * 60 * 60  # Normal time (CET or UTC + 1h)

    return gmtime(utc_secs + delta_secs)