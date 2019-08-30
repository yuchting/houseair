# -*- coding: utf-8 -*-
import requests
import json
from datetime import datetime, timedelta

apihost="http://api.waqi.info/feed/{}/?token={}"
token="032744e8c43746ecfdf1daf2a10f220d1c9a22f5"

def getData(city):
    url = apihost.format(city,token)
    res = requests.get(url)

    if res.status_code == 200 :
        '''
        {
            "status": "ok", 
            "data": {
                "aqi": 82, 
                "idx": 1437, 
                "attributions": [
                    {
                        "url": "http://www.semc.gov.cn/", 
                        "name": "Shanghai Environment Monitoring Center(上海市环境监测中心)"
                    }, 
                    {
                        "url": "http://106.37.208.233:20035/emcpublish/", 
                        "name": "China National Urban air quality real-time publishing platform (全国城市空气质量实时发布平台)"
                    }, 
                    {
                        "url": "https://china.usembassy-china.org.cn/embassy-consulates/shanghai/air-quality-monitor-stateair/", 
                        "name": "U.S. Consulate Shanghai Air Quality Monitor"
                    }, 
                    {
                        "url": "https://waqi.info/", 
                        "name": "World Air Quality Index Project"
                    }
                ], 
                "city": {
                    "geo": [
                        31.2047372, 
                        121.4489017
                    ], 
                    "name": "Shanghai (上海)", 
                    "url": "https://aqicn.org/city/shanghai"
                }, 
                "dominentpol": "pm25", 
                "iaqi": {
                    "co": {
                        "v": 6.4
                    }, 
                    "h": {
                        "v": 81.6
                    }, 
                    "no2": {
                        "v": 12.8
                    }, 
                    "o3": {
                        "v": 11.4
                    }, 
                    "p": {
                        "v": 1007.1
                    }, 
                    "pm10": {
                        "v": 30
                    }, 
                    "pm25": {
                        "v": 82
                    }, 
                    "so2": {
                        "v": 2.6
                    }, 
                    "t": {
                        "v": 28.4
                    }
                }, 
                "time": {
                    "s": "2019-08-26 09:00:00", 
                    "tz": "+08:00", 
                    "v": 1566810000
                }, 
                "debug": {
                    "sync": "2019-08-26T11:00:38+09:00"
                }
            }
        }
        '''
        orgdata = json.loads(res.content)

        if orgdata.get('status') == 'ok' : 
            # organize the data as our format
            '''
            {
                
                'time': datetime.datetime(2019, 8, 26, 10, 0), 
                'date': 
                {
                    'aqi': 74, 
                    'CO': 5.5, 
                    'H': 81.6, 
                    'NO2': 8.7, 
                    'O3': 17.5, 
                    'P': 1007.1, 
                    'PM10': 27, 
                    'PM2.5': 74, 
                    'SO2': 3.1, 
                    'T': 28.4
                }
            }
            '''

            newdata = {}
            orgdata = orgdata['data']
            newdata['time'] = datetime.strptime(orgdata['time']['s'], "%Y-%m-%d %H:%M:%S")

            timezone = orgdata['time']['tz']
            if timezone.find('-') != -1:
                t = datetime.strptime(timezone,"-%H:%M")
                newdata['time'] += timedelta(hours=t.hour,minutes=t.minute)
            elif timezone.find('+') != -1:
                t = datetime.strptime(timezone,"+%H:%M")
                newdata['time'] -= timedelta(hours=t.hour,minutes=t.minute)
            
            data = {'aqi':orgdata['aqi']}
            for k,v in orgdata['iaqi'].items():
                if k == 'pm25':
                    data['PM2.5'] = float(v['v'])
                else:
                    data[k.upper()] = float(v['v'])

            newdata['data'] = data            
            return newdata
        else:
            return None

    else:
        return None
    

if __name__ == "__main__":
    data = getData("shanghai")
    print(datetime.utcnow() - data['time'])
    if data != None:
        print(data)