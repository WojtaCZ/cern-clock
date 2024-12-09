import machine
from machine import Pin
import asyncio

# Set up the pins
BACKLIGHT_PWM = machine.PWM(Pin(16))
BACKLIGHT_PWM.freq(10000)
BACKLIGHT_PWM.duty_u16(0)

# Bezier curve for the smooth fades
async def bezier(timePercentage):
    timePercentage = timePercentage / 100
    return (timePercentage*timePercentage*(3-2*timePercentage))*100

# Sets the percentage of the light
async def setPercent(percent):
    percent = max(min(100, percent), 0)
    BACKLIGHT_PWM.duty_u16(int(65536 * (percent / 100)))

# Fades on from 0% to 100% 
async def fadeOn(duration):
    timePercentage = 0
    while timePercentage <= 100:
        await setPercent(await bezier(timePercentage))
        timePercentage += 1
        await asyncio.sleep_ms(int(duration/100))

# Fades off from 100% to 0%
async def fadeOff(duration):
    timePercentage = 100
    while timePercentage >= 0:
        await setPercent(await bezier(timePercentage))
        timePercentage -= 1
        await asyncio.sleep_ms(int(duration/100))

# Return the status of the light
async def isLit():
    return (BACKLIGHT_PWM.duty_u16() > 0)

def setPercentSync(percent):
    asyncio.run(setPercent(percent))

def fadeOnSync(duration):
    asyncio.run(fadeOn(duration))

def fadeOffSync(duration):
    asyncio.run(fadeOff(duration))

def isLitSync():
    return (BACKLIGHT_PWM.duty_u16() > 0)

