import urequests
import configuration
import logging
logger = logging.getLogger(__name__)

URL = None
status = None

    
def init():
    global URL
   
    URL = configuration.read("vistars_url");
    if URL == None:
        URL = "https://api.ocr.space/parse/imageurl?apikey=K82625374788957&url=https://vistar-capture.s3.cern.ch/lhc1.png"
        logger.warning("Vistars URL not specified, using default.");
    
async def getData():
    global URL
    global status
    
    try:
        response = urequests.get(str(URL), timeout=5)
        data = response.json()['ParsedResults'][0]['ParsedText']
        if data.find("NO BEAM"):
            status = "NO  BEAM"
        else:
            posE = data.find("E:\r\n")
            posGeV = data.find(" GeV")
            status = data[(posE+4):posGeV] + "GEV"
    except:
        status = " CHYBA! ";