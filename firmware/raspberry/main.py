from machine import Pin
from machine import I2C
import time
import network
import socket
import time
import struct

# Decoder reset pin
DECODER_RESETn		 = Pin(2, Pin.OUT);

# These pins control the FIFO on the decoder
FIFO_EN		 = Pin(3, Pin.OUT);
FIFO_R_Wn	 = Pin(1, Pin.OUT);

FIFO_A1		 = Pin(4, Pin.OUT);
FIFO_A0		 = Pin(5, Pin.OUT);

# These pins control the transceiver f| the data
TRCVR_OEn	 = Pin(6, Pin.OUT, value=1);
TRCVR_DIR	 = Pin(7, Pin.OUT, value=0);

# Accelerometer interface
ACCEL_CSn		 = Pin(22, Pin.OUT, value=1);
ACCEL_INT1		 = Pin(20, Pin.IN);
ACCEL_INT2		 = Pin(21, Pin.IN);
ACCEL_SDA		 = Pin(18);
ACCEL_SCL		 = Pin(19);
ACCEL_I2C = I2C(1, freq=100000, scl=ACCEL_SCL, sda=ACCEL_SDA);
ACCEL_I2C_ADD = 25;

# Backlight & buzzer controls
BACKLIGHT_PWM		 = Pin(16, Pin.OUT, value=1)



#BUZZER_PWM		 = machine.PWM(Pin(17));
#BUZZER_PWM.freq(500);
#BUZZER_PWM.duty_u16(50);
#BUZZER_PWM			 = Pin(17, Pin.OUT, value=1)

NTP_DELTA = 2208988800
host = "pool.ntp.org"	

ssid = 'Avenue de Murphy'
password = 'Dommage cest pas possible'

wlan = network.WLAN(network.STA_IF)

taptoggle = 0

def set_time():
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    addr = socket.getaddrinfo(host, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(1)
        res = s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
    finally:
        s.close()
    val = struct.unpack("!I", msg[40:44])[0]
    t = val - NTP_DELTA    
    tm = time.gmtime(t)
    machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6], tm[3] + 1, tm[4], tm[5], 0))

def connect():
    wlan.active(True)
    wlan.connect(ssid, password)

    max_wait = 30
    while max_wait > 0:
        if wlan.status() < 0 or wlan.status() >= 3:
            break
        max_wait -= 1
        print('waiting for connection...')
        time.sleep(1)

    if wlan.status() != 3:
        raise RuntimeError('network connection failed')
    else:
        print('connected')
        status = wlan.ifconfig()
        print( 'ip = ' + status[0] )

def disconnect():
    wlan.active(False)
    wlan.disconnect()
    
    
def accel_init():
    if ACCEL_I2C.readfrom_mem(ACCEL_I2C_ADD, 0x0F, 1)[0] != 0x44:
        print("Accelerometer not detected!");
        return;
    
    print("Accelerometer detected. Setting up tap detection.");
    # Set FS to 2g & enable lownoise
    ACCEL_I2C.writeto_mem(ACCEL_I2C_ADD, 0x25, b'\x04');
    # Tap detect routed to INT1
    ACCEL_I2C.writeto_mem(ACCEL_I2C_ADD, 0x23, b'\x40');   
    # Tap tresholds & enabling
    ACCEL_I2C.writeto_mem(ACCEL_I2C_ADD, 0x30, b'\x04')
    ACCEL_I2C.writeto_mem(ACCEL_I2C_ADD, 0x31, b'\x04')
    ACCEL_I2C.writeto_mem(ACCEL_I2C_ADD, 0x32, b'\xE4');
    # Set shock duration
    ACCEL_I2C.writeto_mem(ACCEL_I2C_ADD, 0x33, b'\x02');
    # Run mode @ 400Hz, high perf|mance
    ACCEL_I2C.writeto_mem(ACCEL_I2C_ADD, 0x20, b'\x74');
    time.sleep(1)
    # Enable interrupts
    ACCEL_I2C.writeto_mem(ACCEL_I2C_ADD, 0x3F, b'\x20');
    
def accel_int1_handler(p):
    global taptoggle
    if taptoggle == 0:
        taptoggle = 1;
    elif taptoggle == 1:
        taptoggle = 0
    return;

def data_read(address):
    FIFO_D0		 = Pin(8, Pin.IN);
    FIFO_D1		 = Pin(10, Pin.IN);
    FIFO_D2		 = Pin(12, Pin.IN);
    FIFO_D3		 = Pin(14, Pin.IN);
    FIFO_D4		 = Pin(9, Pin.IN);
    FIFO_D5		 = Pin(11, Pin.IN);
    FIFO_D6		 = Pin(13, Pin.IN);
    FIFO_D7		 = Pin(15, Pin.IN);


    TRCVR_DIR.value(0);
    
    FIFO_A0.value(address & 1);
    FIFO_A1.value(address & 2);
    FIFO_R_Wn.value(1);
    
    FIFO_EN.value(1);
    TRCVR_OEn.value(0);
    
    byte = (FIFO_D0.value() | (FIFO_D1.value() << 1) | (FIFO_D2.value() << 2)  | (FIFO_D3.value() << 3)  | (FIFO_D4.value() << 4)  | (FIFO_D5.value() << 5)  | (FIFO_D6.value() << 6)  | (FIFO_D7.value() << 7))
     
    TRCVR_OEn.value(1);
    FIFO_EN.value(0);
    
    
    return byte;

def data_write(address, data):
    

    
    FIFO_A0.value(address & 1);
    FIFO_A1.value(address & 2);
    
    FIFO_R_Wn.value(0);
    TRCVR_DIR.value(1);
    
    TRCVR_OEn.value(0);
    
    FIFO_D0		 = Pin(8, Pin.OUT, value=(data & 1));
    FIFO_D1		 = Pin(10, Pin.OUT, value=(data & 2));
    FIFO_D2		 = Pin(12, Pin.OUT, value=(data & 4));
    FIFO_D3		 = Pin(14, Pin.OUT, value=(data & 8));
    FIFO_D4		 = Pin(9, Pin.OUT, value=(data & 16));
    FIFO_D5		 = Pin(11, Pin.OUT, value=(data & 32));
    FIFO_D6		 = Pin(13, Pin.OUT, value=(data & 64));
    FIFO_D7		 = Pin(15, Pin.OUT, value=(data & 128));
    
    FIFO_EN.value(1);
    
    FIFO_EN.value(0);
                                  
    TRCVR_OEn.value(1);
    


def string_write(string):
        while data_read(0) != 1:
            time.sleep_ms(1)
        data_write(0, 0);
        
        time.sleep_ms(5);
        
        data_write(3, ord(string[0]));
        data_write(1, ord(string[1]));
        data_write(2, ord(string[2]));
        data_write(0, ord(string[3]));


        
            
        while data_read(0) != 2:
            time.sleep_ms(1);
            
        data_write(0, 0);
        
        time.sleep_ms(5);
        
        data_write(3, ord(string[4]));
        data_write(1, ord(string[5]));
        data_write(2, ord(string[6]));
        data_write(0, ord(string[7]));


def zfl(s, width):
    return '{:0>{w}}'.format(s, w=width)

    
# Register both accel interrupts
ACCEL_INT1.irq(trigger=Pin.IRQ_RISING, handler=accel_int1_handler);

accel_init();

DECODER_RESETn.value(1);

connect()
set_time()



while True:
    if taptoggle == 0:
        string_write(zfl(str(machine.RTC().datetime()[4]),2) + ":" + zfl(str(machine.RTC().datetime()[5]),2) + ":" + zfl(str(machine.RTC().datetime()[6]),2))
    elif taptoggle == 1:
        string_write(zfl(str(machine.RTC().datetime()[2]),2) + "." + zfl(str(machine.RTC().datetime()[1]),2) + "." + zfl(str(machine.RTC().datetime()[0])[2:4],2))
    time.sleep_ms(50)



    
