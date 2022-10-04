import smbus2
import time
from collections import deque

def get_data(theList, ScaleFactor_A, ScaleFactor_G):
    retrun_value = []
    for i in range(0,6,2):
        if (theList[i+1] & 0x80):
            retrun_value.append((-0x10000 + ((theList[i+1] << 8) | (theList[i]))) / ScaleFactor_G)
        else:
            retrun_value.append(((theList[i+1] << 8) | (theList[i])) / ScaleFactor_G)
    for i in range(6,12,2):
        if (theList[i+1] & 0x80):
            retrun_value.append((-0x10000 + ((theList[i+1] << 8) | (theList[i]))) / ScaleFactor_A)
        else:
            retrun_value.append(((theList[i+1] << 8) | (theList[i])) / ScaleFactor_A)
    return "%.4f, %.4f, %.4f, %.4f, %.4f, %.4f" % (retrun_value[0], retrun_value[1], retrun_value[2], retrun_value[3], retrun_value[4], retrun_value[5])

bus = smbus2.SMBus(1)
address = 0x68
bus.write_byte_data(address, 0x7E, 0xB6) #RESET VALUE
time.sleep(0.1)
bus.write_byte_data(address, 0x7E, 0x11) #ACCELERATION SET NORMAL MODE
time.sleep(0.5)
bus.write_byte_data(address, 0x7E, 0x15) #GYROSCOPE SET NORMAL MODE
time.sleep(0.5)
bus.write_byte_data(address, 0x40, 0x29) #Acc 200 Hz
time.sleep(1)
bus.write_byte_data(address, 0x42, 0x29) #Gyro 200 Hz
time.sleep(1)
bus.write_byte_data(address, 0x41, 0x05) #Acc Range 4g
time.sleep(0.1)
bus.write_byte_data(address, 0x43, 0x03) #Gyro 250 deg/s 
time.sleep(0.1)

ScaleFactor_G = float(131.2)
ScaleFactor_A = float(8192)

bus.write_byte_data(address, 0x47, 0xC0) #FIFO Enable
time.sleep(0.1)
rv = bus.read_byte_data(address, 0x02)
rv = rv & 0x1F
if(rv == 0):
    print("\033[92mOK \033[0m")
else:
    print("%02X" % rv)
    exit()

de = deque()
f = open("file.txt", 'w+', encoding='utf-8')

old_sens_time = float(0)

try:
    while(1):
        block = bus.read_i2c_block_data(address, 0x24, 12)
        de.append(block)
except KeyboardInterrupt:
    for i in range(len(de)):
        if(de[i][0] != 0x00):
            data = get_data(de[i], ScaleFactor_A, ScaleFactor_G)
            f.write(data + '\n')
    f.close()