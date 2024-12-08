import machine
from machine import Pin
import asyncio

BACKLIGHT_PWM = machine.PWM(Pin(16));
BACKLIGHT_PWM.freq(10000);
BACKLIGHT_PWM.duty_u16(0);

active = False

async def setPercent(percent):
    global active
    percent = max(min(100, percent), 0);
    BACKLIGHT_PWM.duty_u16(int(65536 * (percent / 100)));
    if percent > 0:
        active = True
    else:
        active = False

async def bezier(timePercentage):
    timePercentage = timePercentage / 100;
    return (timePercentage*timePercentage*(3-2*timePercentage))*100;

async def fadeOn(duration):
    timePercentage = 0
    while timePercentage <= 100:
        await setPercent(await bezier(timePercentage));
        timePercentage += 1;
        await asyncio.sleep_ms(int(duration/100));
        
async def fadeOff(duration):
    timePercentage = 100
    while timePercentage >= 0:
        await setPercent(await bezier(timePercentage));
        timePercentage -= 1;
        await asyncio.sleep_ms(int(duration/100));