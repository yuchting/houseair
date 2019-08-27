# -*- coding: utf-8 -*-

import threading
import traceback
import uart
import dbagent
import aqicn

from datetime import datetime, timedelta

defaultCity = 'shanghai'
aqicnMeasurement = 'aqicn'
houseMeasurement = 'house'

db = dbagent.DBAgent()
aqicnLeastTime = None

isWritingDb = False

def calcAqi(value, CNOrUS):     
    '''
        check https://www.zhihu.com/question/22206538 for detail of following data values
    '''
    aqiC_us = [
        0,      15.4,
        15.5,   40.4,
        40.5,   65.4,
        65.5,   150.4,
        150.5,  250.4,
        250.5,  350.4,
        350.5,  500.4
    ]

    aqiC_cn = [
        0,      35,
        35,     75,
        75,     115,
        115,    150,
        150,    250,
        250,    350,
        350,    500
    ]

    aqi_index = [
        0,      50,
        51,     100,
        101,    150,
        151,    200,
        201,    300,
        301,    400,
        400,    500
    ]

    
    tableC = aqiC_us
    if CNOrUS :
        tableC = aqiC_cn
    
    result = aqi_index[len(aqi_index) - 1]
    for i in range(0, len(aqi_index) >> 1):
        idx = i << 1
        if value >= tableC[idx] and value < tableC[idx + 1]:
            result = (aqi_index[idx + 1] - aqi_index[idx]) / (tableC[idx + 1] - tableC[idx]) * (value - tableC[idx]) + aqi_index[idx]

    return int(round(result))

def writeAqi():
    data = aqicn.getData(defaultCity)

    global aqicnLeastTime
    if aqicnLeastTime != data['time'] :
        print('write {} measurement, least time {}, data {} '.format(aqicnMeasurement, aqicnLeastTime, data))

        db.insertData(aqicnMeasurement,data['data'], data['time'])
        aqicnLeastTime = data['time']

def init():
    least = db.getLeastData(aqicnMeasurement)
    if least != None:
        global aqicnLeastTime
        aqicnLeastTime = datetime.strptime(least['time'], "%Y-%m-%dT%H:%M:%SZ")
    else:
        writeAqi()    

def wrtingThread(housedata):
    try:
        global aqicnLeastTime
        if datetime.utcnow() - aqicnLeastTime >= timedelta(hours=2):
            writeAqi()

        housedata['PM2.5_cn'] = calcAqi(housedata['PM2.5'], True)
        housedata['PM2.5_us'] = calcAqi(housedata['PM2.5'], False)

        db.insertData(houseMeasurement, housedata)

        print("inserted data: ", housedata)
    except Exception:
        traceback.print_exc()


def loopCallback(housedata):
    if isWritingDb :
        return
    else:
        t = threading.Thread(target=wrtingThread, args=(housedata,))
        t.start() 

if __name__ == '__main__':
    init()
    uart.mainloop(False, loopCallback)
    