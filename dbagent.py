# -*- coding: utf-8 -*-
from influxdb import InfluxDBClient
import datetime

class DBAgent:
        
    def __init__(self, dbhost="127.0.0.1", dbport=8086,dbname="airdb",dbusr="",dbpass=""):
        self.dbclient = InfluxDBClient(dbhost, dbport, dbusr, dbpass, dbname)
        databases = self.dbclient.get_list_database()
        
        hasDefaultDb = False
        for db in databases:
            if db["name"] == dbname:
                hasDefaultDb = True
                break

        if not hasDefaultDb:
            print("create the database:",dbname)
            self.dbclient.create_database(dbname)
            self.dbclient.alter_retention_policy('autogen',dbname,'7d',1,True)  

    def insertData(self, measurement, fields, current_time=None):
        if current_time == None :
            current_time = datetime.datetime.utcnow().isoformat()
        elif type(current_time) is datetime.datetime:
            current_time = current_time.isoformat()

        if not (type(fields) is dict) : 
            raise ValueError("fields must be dict type! but get " + str(type(fields)))

        data = [
            {
                "measurement": measurement,
                "time": current_time,
                "fields": fields,
            }
        ]
        
        self.dbclient.write_points(data)

    def getLeastData(self, measurement):
        query = "select * from {} order by time desc limit 1;".format(measurement)
        result = self.dbclient.query(query)
        datalist = list(result.get_points(measurement=measurement))
        if len(datalist) == 1 : 
            return datalist[0]
        else:
            return None

if __name__ == "__main__":
    db = DBAgent()

    '''
    db.insertData("house", {
                "CO2": 400,
                "CH2O": 3,
                "TVOC": 12,
                "PM2.5":50,
                "PM10":100,
                "Temp":30.5,
                "Humi":50.5
            })

    db.insertData("aqicn", {
                "PM2.5":50,
                "PM10":30,
                "O3":12,
                "NO2":10,
                "SO2":2,
                "CO":5,
                "Temp":28,
                "Humi":80
            })
    '''
    
    print(db.getLeastData("aqicn"))

