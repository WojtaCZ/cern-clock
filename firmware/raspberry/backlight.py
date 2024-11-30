import machine
from machine import Pin

BACKLIGHT_PWM = machine.PWM(Pin(16));
BACKLIGHT_PWM.freq(10000);
BACKLIGHT_PWM.duty_u16(0);

def setPercent(percent):
    percent = max(min(100, percent), 0);
    BACKLIGHT_PWM.duty_u16(int(65536 * (percent / 100)));