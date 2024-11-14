import requests

URL = "https://api.ocr.space/parse/imageurl?apikey=K82625374788957&url=https://vistar-capture.s3.cern.ch/lhc1.png"

def getVistarsData():
    response = requests.get(URL)
    data = response.content()
    data = data[(data.find('"ParsedText": "') + 15) : data.find("ErrorMessage": "")]        
    data = data.split("\r\n")
    return data
