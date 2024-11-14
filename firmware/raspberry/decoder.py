from machine import Pin

# Decoder reset pin
DECODER_RESETn		 = Pin(2, Pin.OUT, value=0);

# These pins control the FIFO on the decoder
FIFO_EN		 = Pin(3, Pin.OUT);
FIFO_R_Wn	 = Pin(1, Pin.OUT);

FIFO_A1		 = Pin(4, Pin.OUT);
FIFO_A0		 = Pin(5, Pin.OUT);

# These pins control the transceiver for the data
TRCVR_OEn	 = Pin(6, Pin.OUT, value=1);
TRCVR_DIR	 = Pin(7, Pin.OUT, value=0);

def assertReset():
    DECODER_RESETn.low();
    
def deassertReset():
    DECODER_RESETn.high();
    
def readData(address):
    # Setup the data pins as inputs
    FIFO_D0		 = Pin(8, Pin.IN);
    FIFO_D1		 = Pin(10, Pin.IN);
    FIFO_D2		 = Pin(12, Pin.IN);
    FIFO_D3		 = Pin(14, Pin.IN);
    FIFO_D4		 = Pin(9, Pin.IN);
    FIFO_D5		 = Pin(11, Pin.IN);
    FIFO_D6		 = Pin(13, Pin.IN);
    FIFO_D7		 = Pin(15, Pin.IN);

    # Set the transceiver direction
    TRCVR_DIR.value(0);
    
    # Write the address
    FIFO_A0.value(address & 1);
    FIFO_A1.value(address & 2);
    
    # Selet read and enable the FIFO output
    FIFO_R_Wn.value(1);
    FIFO_EN.value(1);
    
    # Enable the transceiver
    TRCVR_OEn.value(0);
    
    # Reconstruct the data byte
    byte = (FIFO_D0.value() | (FIFO_D1.value() << 1) | (FIFO_D2.value() << 2)  | (FIFO_D3.value() << 3)  | (FIFO_D4.value() << 4)  | (FIFO_D5.value() << 5)  | (FIFO_D6.value() << 6)  | (FIFO_D7.value() << 7))
    
    # Disable the FIFO and the transceiver
    TRCVR_OEn.value(1);
    FIFO_EN.value(0);
    
    # Return the data
    return byte;

def writeData(address, data):
    # Write the address
    FIFO_A0.value(address & 1);
    FIFO_A1.value(address & 2);
    
    # Select write and set the correct direction
    FIFO_R_Wn.value(0);
    TRCVR_DIR.value(1);
    
    # Enable the transceiver
    TRCVR_OEn.value(0);
    
    # Write out the data
    FIFO_D0		 = Pin(8, Pin.OUT, value=(data & 1));
    FIFO_D1		 = Pin(10, Pin.OUT, value=(data & 2));
    FIFO_D2		 = Pin(12, Pin.OUT, value=(data & 4));
    FIFO_D3		 = Pin(14, Pin.OUT, value=(data & 8));
    FIFO_D4		 = Pin(9, Pin.OUT, value=(data & 16));
    FIFO_D5		 = Pin(11, Pin.OUT, value=(data & 32));
    FIFO_D6		 = Pin(13, Pin.OUT, value=(data & 64));
    FIFO_D7		 = Pin(15, Pin.OUT, value=(data & 128));
    
    # "Clock" the data into the FIFO
    FIFO_EN.value(1);
    FIFO_EN.value(0);
                     
    # Disable the transceiver
    TRCVR_OEn.value(1);


def writeString(string):
        # Wait for the decoder to signal that it expects to receive the first display data
        while readData(0) != 1:
            time.sleep_ms(1)
        
        # Zero out the flag, now, the decoder is waiting until this byte has some value to transfer the data to the displays
        writeData(0, 0);
        
        time.sleep_ms(5);
        
        # Write the display data to the buffer
        writeData(3, ord(string[0]));
        writeData(1, ord(string[1]));
        writeData(2, ord(string[2]));
        writeData(0, ord(string[3]));
        
        # Wait for the decoder to signal that it expects to receive the second display data
        while readData(0) != 2:
            time.sleep_ms(1);
        
        # Zero out the flag, now, the decoder is waiting until this byte has some value to transfer the data to the displays
        writeData(0, 0);
        
        time.sleep_ms(5);
        
        # Write the display data to the buffer
        writeData(3, ord(string[4]));
        writeData(1, ord(string[5]));
        writeData(2, ord(string[6]));
        writeData(0, ord(string[7]));


# Function for zero padding
def zfl(s, width):
    return '{:0>{w}}'.format(s, w=width)