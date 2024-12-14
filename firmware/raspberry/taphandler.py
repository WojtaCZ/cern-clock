import decoder
import ntp
import backlight
import vistars
import asyncio
import time
import accelerometer

screen = 0
light = False
vdata = None

async def vistarsFetch():
    global vdata
    global screen

    vdata = await vistars.getData()   
    if vdata != "NO  BEAM":
        vdata = (decoder.zfl(str(vdata),5) + "GEV");
    
    screen = 3;
    
async def loadScreen():
    decoder.writeString("O       ");
    await asyncio.sleep_ms(50)
    decoder.writeString(" O      ");
    await asyncio.sleep_ms(50)
    decoder.writeString("  O     ");
    await asyncio.sleep_ms(50)
    decoder.writeString("   O    ");
    await asyncio.sleep_ms(50)
    decoder.writeString("    O   ");
    await asyncio.sleep_ms(50)
    decoder.writeString("     O  ");
    await asyncio.sleep_ms(50)
    decoder.writeString("      O ");
    await asyncio.sleep_ms(50)
    decoder.writeString("       O");
    await asyncio.sleep_ms(50)
    decoder.writeString("      O ");
    await asyncio.sleep_ms(50)
    decoder.writeString("     O  ");
    await asyncio.sleep_ms(50)
    decoder.writeString("    O   ");
    await asyncio.sleep_ms(50)
    decoder.writeString("   O    ");
    await asyncio.sleep_ms(50)
    decoder.writeString("  O     ");
    await asyncio.sleep_ms(50)
    decoder.writeString(" O      ");
    await asyncio.sleep_ms(50)
        
async def tapHandler(tapnum):
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
            

async def displayLoop():
    global vdata
    global screen
    while True:
        print("Hello")
        

        
        if screen == 0 or screen == 1:
                timeTuple = await ntp.localTime();
                    
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
        elif screen == 3:
            decoder.writeString("12345678");
      
                
        