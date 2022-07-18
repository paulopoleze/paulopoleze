from threading import Thread
import functools
import time

from iqoptionapi.stable_api import IQ_Option
import time
from datetime import datetime
import pathlib
import mysql.connector
    
##ORQUESTRADOR
def timeout(seconds_before_timeout):
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = [Exception('function [%s] timeout [%s seconds] exceeded!' % (func.__name__, seconds_before_timeout))]
            def newFunc():
                try:
                    res[0] = func(*args, **kwargs)
                except Exception as e:
                    res[0] = e
            t = Thread(target=newFunc)
            t.daemon = True
            try:
                t.start()
                t.join(seconds_before_timeout)
            except Exception as e:
                print('error starting thread')
                raise e
            ret = res[0]
            if isinstance(ret, BaseException):
                raise ret
            return ret
        return wrapper
    return deco

ultimaHora = 99
ultimaHora_02 = 99
ultimaHora_03 = 99
OTC_Candles = ["EURUSD-OTC","AUDCAD-OTC","EURJPY-OTC","EURGBP-OTC", "GBPUSD-OTC", "NZDUSD-OTC", "USDCHF-OTC", "GBPJPY-OTC", "USDJPY-OTC"]
#OTC_Candles = ["ETHUSD", "BTCUSD", "XRPUSD", "EOSUSD", "LTCUSD","GBPUSD","USDCAD","USDCHF","AUDUSD","AUDJPY","EURJPY","GBPJPY","USDJPY","EURGBP","AUDCAD", "EURUSD", "GBPCAD", "EURNZD", "AUDNZD", "USDNOK", "GBPCHF", "GBPNZD", "AUDCHF", "CADCHF", "GBPAUD"]
data = 0
I_want_money=IQ_Option("xelosi3032@ateampc.com","oluapPAULO321")
I_want_money.connect()#connect to iqoption
codigos = I_want_money.get_all_ACTIVES_OPCODE()

print("Conectado")

@timeout(7)
def opcodes():
    global codigos
    codigos = I_want_money.get_all_ACTIVES_OPCODE()
    return True

@timeout(7)
def conectariq():
    global I_want_money
    I_want_money=IQ_Option("xelosi3032@ateampc.com","oluapPAULO321")
    I_want_money.connect()#connect to iqoption
    return True

@timeout(7)
def getcandles(tempo,timestamp,Candles_OTC):
    #60 1 minuto
    #300 5 minutos
    #900 15 minutos
    global I_want_money
    global data
    data = I_want_money.get_candles(Candles_OTC, tempo, 1, timestamp)

while True:
    
    end_from_time=time.time()-60
    end_from_time_02 = time.time()-300
    end_from_time_03 = time.time()-900
    dt_object = datetime.fromtimestamp(end_from_time)
    horaCorrigida = dt_object.replace(second = 0)
    timestamp = datetime.timestamp(horaCorrigida)
#    I_want_money.connect()

#    while True:
#        try:
#            opcodes()
#            break
#        except:
#            try:
#                conectariq()
#            except:
#                True            
#            True
    
    if horaCorrigida.minute != ultimaHora:
        mydb = mysql.connector.connect(
          host="localhost",
          user="root",
          password="poleze",
          database="candles"
        )

        mysqlCon = mydb.cursor()
        time.sleep(1)
        ultimaHora = horaCorrigida.minute
        for Candles_OTC in OTC_Candles:
                while True:
                    try:
                        getcandles(60,timestamp,Candles_OTC)
                        break
                    except:
                        try:
                            conectariq()
                            print("deu ruim")
                        except:
                            print("Repeteco 1")
                            True
                            
                        print("Repeteco 2")
                        True
                #print("to passando")   
                if data[0]["open"] > data[0]["close"]:
                    print(Candles_OTC)
                    print("1 - Candle de Venda")
                    print("Abertura:",data[0]["open"])
                    print("Fechamento:", data[0]["close"])
                    sql = "INSERT INTO candles (paridade, abertura, fechamento, condicao, data) VALUES (%s,%s,%s,%s,%s)"
                    val = (Candles_OTC, data[0]["open"], data[0]["close"], "-1", horaCorrigida)
                    mysqlCon.execute(sql, val)
                    mydb.commit()
                    
                elif data[0]["open"] < data[0]["close"]:
                    print(Candles_OTC)
                    print("1 - Candle de Compra")
                    print("Abertura:",data[0]["open"])
                    print("Fechamento:", data[0]["close"])
                    sql = "INSERT INTO candles (paridade, abertura, fechamento, condicao, data) VALUES (%s,%s,%s,%s,%s)"
                    val = (Candles_OTC, data[0]["open"], data[0]["close"], "1", horaCorrigida)
                    mysqlCon.execute(sql, val)
                    mydb.commit()
                else:
                    print("Doji")
                    sql = "INSERT INTO candles (paridade, abertura, fechamento, condicao, data) VALUES (%s,%s,%s,%s,%s)"
                    val = (Candles_OTC, data[0]["open"], data[0]["close"], "50", horaCorrigida)
                    mysqlCon.execute(sql, val)
                    mydb.commit()

        mydb.close()
        mysqlCon.close()
        print("Finalizado M1 - Hora:",horaCorrigida)

    dt_object_02 = datetime.fromtimestamp(end_from_time_02)
    horaCorrigida_02 = dt_object_02.replace(second = 0)
    timestamp_02 = datetime.timestamp(horaCorrigida_02)
    
    if horaCorrigida_02.minute != ultimaHora_02 and (horaCorrigida_02.minute % 5 == 0 or horaCorrigida_02.minute == 0):        
        #time.sleep(5)
        mydb = mysql.connector.connect(
          host="localhost",
          user="root",
          password="poleze",
          database="candles"
        )

        mysqlCon = mydb.cursor()
        ultimaHora_02 = horaCorrigida_02.minute
        for Candles_OTC in OTC_Candles:
                while True:
                    try:
                        getcandles(300,timestamp_02,Candles_OTC)
                        break
                    except:
                        try:
                            conectariq()
                            print("deu ruim")
                        except:
                            print("Repeteco 1")
                            True
                            
                        print("Repeteco 2")
                        True
                
                if data[0]["open"] > data[0]["close"]:
                    print(Candles_OTC)
                    print("1 - Candle de Venda")
                    print("Abertura:",data[0]["open"])
                    print("Fechamento:", data[0]["close"])
                    sql = "INSERT INTO candles_m5 (paridade, abertura, fechamento, condicao, data) VALUES (%s,%s,%s,%s,%s)"
                    val = (Candles_OTC, data[0]["open"], data[0]["close"], "-1", horaCorrigida_02)
                    mysqlCon.execute(sql, val)
                    mydb.commit()
                    
                elif data[0]["open"] < data[0]["close"]:
                    print(Candles_OTC)
                    print("1 - Candle de Compra")
                    print("Abertura:",data[0]["open"])
                    print("Fechamento:", data[0]["close"])
                    sql = "INSERT INTO candles_m5 (paridade, abertura, fechamento, condicao, data) VALUES (%s,%s,%s,%s,%s)"
                    val = (Candles_OTC, data[0]["open"], data[0]["close"], "1", horaCorrigida_02)
                    mysqlCon.execute(sql, val)
                    mydb.commit()
                else:
                    print("Doji")
                    sql = "INSERT INTO candles_m5 (paridade, abertura, fechamento, condicao, data) VALUES (%s,%s,%s,%s,%s)"
                    val = (Candles_OTC, data[0]["open"], data[0]["close"], "50", horaCorrigida_02)
                    mysqlCon.execute(sql, val)
                    mydb.commit()
                    
        mydb.close()
        mysqlCon.close()
        print("Finalizado M5 - Hora:",horaCorrigida)


    
    dt_object_03 = datetime.fromtimestamp(end_from_time_03)
    horaCorrigida_03 = dt_object_03.replace(second = 0)
    timestamp_03 = datetime.timestamp(horaCorrigida_03)
    
    if horaCorrigida_03.minute != ultimaHora_03 and (horaCorrigida_03.minute % 15 == 0 or horaCorrigida_03.minute == 0):        
        #time.sleep(5)
        mydb = mysql.connector.connect(
          host="localhost",
          user="root",
          password="poleze",
          database="candles"
        )

        mysqlCon = mydb.cursor()
        ultimaHora_03 = horaCorrigida_03.minute
        for Candles_OTC in OTC_Candles:
                while True:
                    try:
                        getcandles(900,timestamp_03,Candles_OTC)
                        break
                    except:
                        try:
                            conectariq()
                            print("deu ruim")
                        except:
                            print("Repeteco 1")
                            True
                            
                        print("Repeteco 2")
                        True
                        
                if data[0]["open"] > data[0]["close"]:
                    print(Candles_OTC)
                    print("1 - Candle de Venda")
                    print("Abertura:",data[0]["open"])
                    print("Fechamento:", data[0]["close"])
                    sql = "INSERT INTO candles_m15 (paridade, abertura, fechamento, condicao, data) VALUES (%s,%s,%s,%s,%s)"
                    val = (Candles_OTC, data[0]["open"], data[0]["close"], "-1", horaCorrigida_03)
                    mysqlCon.execute(sql, val)
                    mydb.commit()
                    
                elif data[0]["open"] < data[0]["close"]:
                    print(Candles_OTC)
                    print("1 - Candle de Compra")
                    print("Abertura:",data[0]["open"])
                    print("Fechamento:", data[0]["close"])
                    sql = "INSERT INTO candles_m15 (paridade, abertura, fechamento, condicao, data) VALUES (%s,%s,%s,%s,%s)"
                    val = (Candles_OTC, data[0]["open"], data[0]["close"], "1", horaCorrigida_03)
                    mysqlCon.execute(sql, val)
                    mydb.commit()
                else:
                    print("Doji")
                    sql = "INSERT INTO candles_m15 (paridade, abertura, fechamento, condicao, data) VALUES (%s,%s,%s,%s,%s)"
                    val = (Candles_OTC, data[0]["open"], data[0]["close"], "50", horaCorrigida_03)
                    mysqlCon.execute(sql, val)
                    mydb.commit()
        mydb.close()
        mysqlCon.close()
        print("Finalizado M15 - Hora:",horaCorrigida)
        True
    
