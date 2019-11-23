# -*- coding: utf-8 -*
import serial
import time
import uart

MAX_READ_COUNT = 42
AVERAGE_TIMES = 5
READ_INTERVAL = 2.0 # in seconds
READ_DATA_ATTEMPTS = 2

SEND_DATA = b'\x42\x4D\xAC\x00\x00\x01\x3B'

# initialize the serial port
ser = serial.Serial("/dev/ttyS0", 9600)

serialdata = b""
datalist = []

def checkData(serialdata, printInfo=False):
    
    if len(serialdata) < MAX_READ_COUNT:
        if printInfo :
            print("len(serialdata) < MAX_READ_COUNT")
        return False

    sum = 0
    for i in range(0, MAX_READ_COUNT - 2):
        if printInfo : 
            print("{:x}".format(serialdata[i]),end=" ")

        sum += int(serialdata[i])
        
    verify = int(serialdata[MAX_READ_COUNT - 2]) * 256 + int(serialdata[MAX_READ_COUNT - 1])
    
    if printInfo : 
        print("sum = {:x}, verify = {:x}".format(sum, verify))
    
    return sum == verify


def parseNegative(high, low):
    negative = False
    if high & 0x80 != 0:
        negative = True
        high &= 0x7f

    temp = (float(high) * 256 + float(low)) / 10

    if negative : 
        temp = -temp
    return temp
    

def mainloop(printInfo, callback=None):
    try:
        while True:
            
            if printInfo : 
                print("\nwrite command")
                
            ser.write(SEND_DATA)
            ser.flushOutput()

            attemptCount = 0
            
            while attemptCount < READ_DATA_ATTEMPTS:
                
                # wait for second
                time.sleep(READ_INTERVAL)
                                
                if ser.inWaiting() >= 0:
                    
                    if printInfo : 
                        print("read data")
                
                    global serialdata
                    serialdata = serialdata + ser.read_all()

                    if len(serialdata) >= MAX_READ_COUNT :
                        if checkData(serialdata) :

                            data = {}
                            data['PM1.0'] = int(serialdata[10]) * 256 + int(serialdata[11])
                            data['PM2.5'] = int(serialdata[12]) * 256 + int(serialdata[13])
                            data['PM10'] = int(serialdata[14]) * 256 + int(serialdata[15])
                            data['TVOC'] = (int(serialdata[28]) * 256 + int(serialdata[29])) / 100.0
                            data['CH2O'] = (int(serialdata[31]) * 256 + int(serialdata[32])) / 100.0
                            data['CO2'] = int(serialdata[34]) * 256 + int(serialdata[35])
                            data['T'] = parseNegative(int(serialdata[36]), int(serialdata[37]))
                            data['Humi'] = parseNegative(int(serialdata[38]), int(serialdata[39]))

                            if printInfo : 
                                print("PM1.0: {} ug/m^3".format(data['PM1.0']))
                                print("PM2.5: {} ug/m^3".format(data['PM2.5']))
                                print("PM10: {} ug/m^3".format(data['PM10']))
                                print("CO2: {} ppm".format(data['CO2']))
                                print("CH2O: {} mg/m^3".format(data['CH2O']))
                                print("TVOC: {} ppm".format(data['TVOC']))                                
                                print("Temp: {:.1f} C".format(data['T']))
                                print("Humi: {:.1f} %".format(data['Humi']))

                            datalist.append(data)

                            if len(datalist) >= AVERAGE_TIMES:
                                aver = uart.average(datalist)
                                if printInfo :
                                    print("average: ", aver)
                                    
                                if callback != None:
                                    callback(aver)
                                    
                                datalist.clear()
                            
                            serialdata = b""

                        else:
                            print("Checked error serialdata!")
                            checkData(serialdata, True)
                            attemptCount = READ_DATA_ATTEMPTS
                            break
                        
                        break   
                    else:
                        if printInfo : 
                            print("received {} data, wait for others".format(len(serialdata)))
                
                attemptCount += 1
                   
            if attemptCount >= READ_DATA_ATTEMPTS:
                # reset all data when it's over fixed read attempts
                serialdata = b""
                ser.flushInput()
                time.sleep(READ_INTERVAL)
                
                if printInfo:
                    print("\n!!!!!! cannot read any data by {} attempts\n".format(READ_DATA_ATTEMPTS))
                    
    except Exception as ex:
        print(ex)
    finally:
        if ser != None:
            ser.close()
    

if __name__ == '__main__':
    mainloop(True)

        
