from machine import Pin
import machine
import asyncio
import time

# Init the buzzer pins
BUZZER_PWM = machine.PWM(Pin(17))
BUZZER_PWM.duty_u16(0)

# Beep at set frequency for specific duration
def beep(frequency, duration):
    BUZZER_PWM.freq(frequency)
    BUZZER_PWM.duty_u16(int(65535/2))
    time.sleep_ms(duration)
    BUZZER_PWM.duty_u16(0)

# The OK beep
def beepOK():
    beep(800, 100)
    beep(1000, 100)

# The ERROR beep
def beepERR():
    beep(1000, 100)
    beep(800, 100)