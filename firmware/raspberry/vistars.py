import urequests
import configuration
import logging
logger = logging.getLogger(__name__)

URL = None
status = None

# Load the vistars config
def init():
    global URL
   
    URL = configuration.read("vistars_url")
    if URL == None:
        URL = "https://api.ocr.space/parse/imageurl?apikey=K82625374788957&url=https://vistar-capture.s3.cern.ch/lhc1.png"
        logger.warning("Vistars URL not specified, using default.")
    
# Get the data
async def getData():
    global URL
    global status
    
    try: 
        # Call the OCR service
        response = urequests.get(str(URL), timeout=5)
        data = response.json()['ParsedResults'][0]['ParsedText']

        # If there is a mention of "NO BEAM", there is no need to look for energy
        if data.find("NO BEAM"):
            status = "NO  BEAM"
        
        # Though if there is energy, return that
        else:
            posE = data.find("E:\r\n")
            posGeV = data.find(" GeV")
            status = data[(posE+4):posGeV] + "GEV"

    except:
        # In all other cases, return error
        status = " CHYBA! "