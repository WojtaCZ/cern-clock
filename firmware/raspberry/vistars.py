import urequests

URL = "https://api.ocr.space/parse/imageurl?apikey=K82625374788957&url=https://vistar-capture.s3.cern.ch/lhc1.png"

def getData():
    global URL
    response = urequests.get(URL)
    data = response.json()['ParsedResults'][0]['ParsedText']
    if data.find("NO BEAM"):
        return "NO  BEAM"
    else:
        posE = data.find("E:\r\n")
        posGeV = data.find(" GeV")
        return data[(posE+4):posGeV]
