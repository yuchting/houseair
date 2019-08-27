# -*- coding: utf-8 -*
import serial
import time

MAX_READ_COUNT = 17
AVERAGE_TIMES = 5

# 打开串口
ser = serial.Serial("/dev/ttyS0", 9600)
serialdata = b''
datalist = []

def average(datalist):
    length = len(datalist)
    if len(datalist) == 0 :
        raise ValueError("the length of datalist must be greater and equal then 1")

    result = {}
    keys = datalist[0].keys()
    for k in keys:
        sum = 0.0
        for i in datalist:
            sum += i[k]
        sum = round(sum/length,1)
        
        if type(i[k]) is int :
            sum = int(sum)
            
        result[k] = sum

    return result

def checkData(serialdata, printInfo=False):
    '''
    check the serialdata by the rule:
    https://img.alicdn.com/imgextra/i3/605658691/O1CN01OirvSU2E4WiAoubXN_!!605658691.jpg
    '''
    if len(serialdata) < MAX_READ_COUNT:
        if printInfo :
            print("len(serialdata) < MAX_READ_COUNT")
        return False

    sum = 0
    for i in range(0, MAX_READ_COUNT - 1):
        if printInfo : 
            print("{:x}".format(serialdata[i]),end=" ")

        sum += serialdata[i]

    if printInfo : 
        print("sum before {:x}".format(sum))

    sum = sum & 0xff

    if printInfo : 
        print("sum after {:x}".format(sum))
        print("serialdata[MAX_READ_COUNT - 1] {:x}".format(serialdata[MAX_READ_COUNT - 1]))
    
    return sum == serialdata[MAX_READ_COUNT - 1]


def parseTemperature(serialdata):
    tempHigher = int(serialdata[12])
    negative = False
    if tempHigher & 0x80 != 0:
        negative = True
        tempHigher &= 0x7f

    temp = float(tempHigher) + float(int(serialdata[13])) / 10

    if negative : 
        temp = -temp
    return temp
    

def mainloop(printInfo, callback=None):
    try:
        while True:
            # 获得接收缓冲区字符
            if ser.inWaiting() >= 0:
                # 读取内容并回显
                global serialdata
                serialdata = serialdata + ser.read_all()

                if len(serialdata) >= MAX_READ_COUNT :
                    if checkData(serialdata) :

                        data = {}
                        data['CO2'] = int(serialdata[2]) * 256 + int(serialdata[3])
                        data['CH2O'] = int(serialdata[4]) * 256 + int(serialdata[5])
                        data['TVOC'] = int(serialdata[6]) * 256 + int(serialdata[7])
                        data['PM2.5'] = int(serialdata[8]) * 256 + int(serialdata[9])
                        data['PM10'] = int(serialdata[10]) * 256 + int(serialdata[11])
                        data['T'] = parseTemperature(serialdata)
                        data['Humi'] = float(int(serialdata[14])) + float(int(serialdata[15])) / 10

                        if printInfo : 
                            print("CO2: {} ppm".format(data['CO2']))
                            print("CH2O: {} ug/m^3".format(data['CH2O']))
                            print("TVOC: {} ug/m^3".format(data['TVOC']))
                            print("PM2.5: {} ug/m^3".format(data['PM2.5']))
                            print("PM10: {} ug/m^3".format(data['PM10']))
                            print("Temp: {:.1f} C".format(data['T']))
                            print("Humi: {:.1f} %".format(data['Humi']))

                        datalist.append(data)

                        if len(datalist) >= AVERAGE_TIMES:
                            aver = average(datalist)
                            if printInfo :
                                print("average: ", aver)
                                
                            if callback != None:
                                callback(aver)
                                
                            datalist.clear()
                        
                        serialdata = serialdata[MAX_READ_COUNT:]

                    else:
                        print("Checked error serialdata!")
                        checkData(serialdata, True)
                        serialdata = b""
                    
                    if printInfo : 
                        print("")                   
                
            # 必要的软件延时
            time.sleep(0.1)
            
    except Exception as ex:
        print(ex)
    finally:
        if ser != None:
            ser.close()
    

if __name__ == '__main__':
    mainloop(True)

        