from machine import Pin
import machine
import asyncio
import time

BUZZER_PWM = machine.PWM(Pin(17));
BUZZER_PWM.duty_u16(0);

def beep(frequency, duration):
    BUZZER_PWM.freq(frequency);
    BUZZER_PWM.duty_u16(int(65535/2));
    time.sleep_ms(duration)
    BUZZER_PWM.duty_u16(0);
    
def beepOK():
    beep(800, 100)
    beep(1000, 100)

def beepERR():
    beep(1000, 100)
    beep(800, 100)