import logging
import os
import io

logger = logging.getLogger(__name__)

CONFIG_FILE = "configuration.conf"

def findPosition(data, key):
    totalPos = 0    
    while True:
        position = data.find(key + "=\"")
        # If the data is not on the first line or doesnt start wih newline, consider it as other text
        if (position > 0 and data[position-1] != '\n'):
            # Remove the preceeding text from the data
            keyLen = len(key + "=\"")
            data = data[(position + keyLen):]
            totalPos += position + keyLen
        else:
            if position == -1:
                return -1
            else:
                return totalPos+position

def read(key):
    key = str(key)
    try:
        f=open(CONFIG_FILE,"r")
    except:
        logger.error("Configuration file not found on the filesystem!")
        return None
    
    contents = f.read()
    f.close()
    
    position = findPosition(contents, key)
    
    if position == -1:
        return None
        
    data = contents[(position + len(key) + 2) :].split('\n', 1)[0]
    if data[:-1] == '':
        return None
    
    return data[:-1]

    

def write(key, data):
    data = str(data)
    key = str(key)
    try:
        f = open(CONFIG_FILE,"r")
    except:
        raise Exception("Configuration file not found on the filesystem!")
    
    contents = f.read()
    f.close()
    
    position = findPosition(contents, key)
    
    oldData = contents[position:].split('\n', 1)[0]
    newData = key + "=\"" + data + "\""
    
    if position == -1:
        # If the key is not already present
        # Go to the end of file and write the key
        f = open(CONFIG_FILE,"a")
        f.write(newData)
    else:
        # If the key is present in the file
        # Replace it with the new data
        f = open(CONFIG_FILE,"w")
        contents = contents.replace(oldData, newData)
        f.write(contents)
    
    f.close()
    
    return newData


def update(key, data):
    data = str(data)
    key = str(key)

    try:
        f = open(CONFIG_FILE,"r")
    except:
        raise Exception("Configuration file not found on the filesystem!")
    
    contents = f.read()
    f.close()
    
    position = findPosition(contents, key)

    oldData = contents[position:].split('\n', 1)[0]
    newData = key + "=\"" + data + "\""
    
    if position != -1:
        # If the key is present in the file
        # Replace it with the new data
        f = open(CONFIG_FILE,"w")
        contents = contents.replace(oldData, newData)
        f.write(contents)
        f.close()

        return newData
    else:
        return None
    
    
