import decoder
import ntp
import backlight
import vistars
import uasyncio
import time
import accelerometer

screen = 0
light = False
vdata = None

def vistarsFetch():
    global vdata
    global screen

    vdata = vistars.getData()   
    if vdata != "NO  BEAM":
        vdata = (decoder.zfl(str(vdata),5) + "GEV");
    
    screen = 3;
    
def loadScreen():
    decoder.writeString("O       ");
    time.sleep_ms(50)
    decoder.writeString(" O      ");
    time.sleep_ms(50)
    decoder.writeString("  O     ");
    time.sleep_ms(50)
    decoder.writeString("   O    ");
    time.sleep_ms(50)
    decoder.writeString("    O   ");
    time.sleep_ms(50)
    decoder.writeString("     O  ");
    time.sleep_ms(50)
    decoder.writeString("      O ");
    time.sleep_ms(50)
    decoder.writeString("       O");
    time.sleep_ms(50)
    decoder.writeString("      O ");
    time.sleep_ms(50)
    decoder.writeString("     O  ");
    time.sleep_ms(50)
    decoder.writeString("    O   ");
    time.sleep_ms(50)
    decoder.writeString("   O    ");
    time.sleep_ms(50)
    decoder.writeString("  O     ");
    time.sleep_ms(50)
    decoder.writeString(" O      ");
    time.sleep_ms(50)
        
def tapHandler(tapnum):
    global screen
    global vdata
    global light
    
    if tapnum == 1:
        screen += 1;
                    
        if screen == 2:
            vdata = None;
            vistarsFetch()
                    
        if screen == 4:
                screen = 0;
    else:
        light = not light;
        if light:
            backlight.setPercent(100);
        else:
            backlight.setPercent(0);
            

def screenHandler(p):
    global vdata
    global screen
    
    if screen == 0 or screen == 1:
            timeTuple = ntp.localTime();
                
            year = timeTuple[0]
            month = timeTuple[1]
            day = timeTuple[2]
                
            hour = timeTuple[3]
            minute = timeTuple[4]
            second = timeTuple[5]
            if screen == 0:
                decoder.writeString(decoder.zfl(str(hour),2) + ":" + decoder.zfl(str(minute),2) + ":" + decoder.zfl(str(second),2))
            else:
                decoder.writeString(decoder.zfl(str(day),2) + "." + decoder.zfl(str(month),2) + "." + str(year)[-2:])
    elif screen == 2:
        loadScreen();
    elif screen == 3:
        decoder.writeString("12345678");
      
                
        