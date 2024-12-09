import tinyweb
import configuration
import clock
import decoder
import buzzer

app = tinyweb.webserver()

# Function to dynamically generate a information response 
async def infoResponse(data):
    return """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <link rel="stylesheet" href="style.css">
                <title>CERN CLOCK</title>
            </head>
            <body class="quicksand-light instructions" >
                <div class="content">
            """ + data + """
                </div>
                
            </body>
            </html>
            """

# Class to GET and POST configuration parameters
class parameters():
    # Go through all the keys in the GET request and return their values as a dictionary
    def get(self, data):
        resp = {}

        for key in data:
            resp[key] = configuration.read(key)
            
        return resp

    # Go through all the keys in the POST request and update the configuration accordingly, than, return the updated values
    def post(self, data):
        resp = {}

        for key in data:
            configuration.update(key, data[key])
        
        for key in data:
            resp[key] = configuration.read(key)
            
        return resp, 201

# Class to POST wifi setup
class parameters():
    # Go through all the keys in the POS request and update the configuration accordingly, than, return the updated values
    def post(self, data):
        resp = {}

        for key in data:
            configuration.update(key, data[key])
        
        for key in data:
            resp[key] = configuration.read(key)
            
        return resp, 201

# Add the parameters as a resource
app.add_resource(parameters, "/parameters")

# Add the route to stylesheet
@app.route('/style.css')
async def style(request, response):
    await response.send_file("website/style.css")

# Add the route to root
@app.route('/')
async def index(request, response):
    await response.send_file("website/index.html")

# Add the route to the connection form
@app.route('/connect.html')
async def connect(request, response):
    await response.send_file("website/connect.html")

# Add the route to the parameter setup page
@app.route('/params.html')
async def params(request, response):
    await response.send_file("website/params.html")

# Add the route to the restart page
@app.route('/restart.html')
async def restart(request, response):
    await response.send_file("website/restart.html")
    buzzer.beepOK()
    clock.restart()

# Add the route to the WIFI setup POST method
@app.route('/setwifi', methods = ['POST'], max_body_size = 2048, save_headers = ["Content-Length","Content-Type"], allowed_access_control_headers = ["Content-Length","Content-Type"])
async def connect(request, response):
    # Parse the request
    data = await request.read_parse_form_data()

    try:
        # Get the data and update the config
        ssid = data["ssid"]
        password = data["pass"]
        
        configuration.update("wifi_ssid", ssid)
        configuration.update("wifi_password", password)
        
        # Send the info response
        await response.start_html()
        await response.send(await infoResponse("""
            <span class="quicksand-bold">Připojuji k WiFi...</span><br>
            <span class="quicksand-medium">""" + ssid + """</span>
        """))
        
        # Display a message on the decoder, beep and reset to apply
        buzzer.beepOK()
        clock.restart()
        
    except:
        # The data had wrong format, send the info page
        await response.start_html()
        await response.send(await infoResponse("""
            <span class="quicksand-bold">Chybně zaslaná data!</span><br>
        """))

        # Beep to signal an error
        buzzer.beepERR()
    
    
   