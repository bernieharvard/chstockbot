import getopt, sys, config,os
import pandas as pd
from pandas import DataFrame
import pandas_datareader.data as web
import datetime
from requests.exceptions import ConnectionError
from telegram import Bot
from pandas_datareader._utils import RemoteDataError 

symbols= [["SPY", 10,50],["QQQ",13,55,200],["IWM", 13,55,200],["RBLX", 13,55,200]]
notifychat = -1001484528239
adminchat = -1001484528239
dss=['stooq','yahoo']

def help():
    return "'sendxyh.py -c cofigpaht'"

def cal_symbols_avg_stooq(symbol:str,avgs:list):
    
    start = datetime.date.today() - datetime.timedelta(days=365)
    end = datetime.date.today()
    
    try:
        for ds in dss:
            if ds == 'stooq':
                df = web.DataReader(symbol.upper(), ds, start=start, end=end) 
                message = f"{symbol.upper()}价格：{df['Close'][0]:0.2f}({df['Low'][0]:0.2f}-{df['High'][0]:0.2f}) \n"       
                if end == df.index[0]:
                    for avg in avgs:
                        if df.count()[0] > avg :
                            if df['Close'][0] > df.head(avg)['Close'].mean() :
                                message += f"🟢{avg} 周期均价:{df.head(avg)['Close'].mean():0.2f}\n"
                            elif df['Close'][0] < df.head(avg)['Close'].mean() :
                                message += f"🔴{avg} 周期均价:{df.head(avg)['Close'].mean():0.2f}\n"
                        else:
                            message += f"{avg}周期均价因时常不足无法得出\n"    
                    return f"{message}\n"
            else:
                        return f"今天不是交易日\n"    
    except RemoteDataError:
        return f"{symbol}丢失了\n"
        

def cal_symbols_avg_yahoo(symbol:str,avgs:list):
    
    start = datetime.date.today() - datetime.timedelta(days=365)
    end = datetime.date.today()
    
    try:
        for ds in dss:
            if ds == "yahoo":
                df = web.DataReader(symbol.upper(), ds, start=start, end=end)
                message = f"{symbol.upper()}价格：{df['Adj Close'][-1]:0.2f}({df['Low'][-1]:0.2f}-{df['High'][-1]:0.2f}) \n"
                if end == df.index[-1]:
                    for avg in avgs:
                        if df.count()[0] > avg :
                            if df['Close'][0] > df.head(avg)['Close'].mean() :
                                message += f"🟢{avg} 周期均价:{df.tail(avg)['Adj Close'].mean():0.2f}\n"
                            elif df['Close'][0] < df.head(avg)['Close'].mean() :
                                message += f"🔴{avg} 周期均价:{df.head(avg)['Adj Close'].mean():0.2f}\n"
                        else:
                            message += f"{avg}周期均价因时常不足无法得出\n"   
                    return f"{message}\n"
            else:
                return f"今天不是交易日\n"    
    except RemoteDataError:
        return f"{symbol}丢失了\n"


    
if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:", ["config="])
    except getopt.GetoptError:
        print(help())
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print(help())
            sys.exit()
        elif opt in ("-c", "--config"):
            config.config_path = arg          

    config.config_file = os.path.join(config.config_path, "config.json")
    try:
        CONFIG = config.load_config()
    except FileNotFoundError:
        print(f"config.json not found.Generate a new configuration file in {config.config_file}")
        config.set_default()
        sys.exit(2)

    bot = Bot(token = CONFIG['Token'])

    message = "🌈🌈🌈当日天相🌈🌈🌈: \n"
    try: 
        for symbol in symbols:
            message += cal_symbols_avg_yahoo(symbol[0],symbol[1:])
        bot.send_message(notifychat,message)
        bot.send_message(adminchat,f"{notifychat}向发送成功夕阳红:\n{message}")
    except Exception as err:
        bot.send_message(adminchat,f"今天完蛋了，yahoo什么都不知道，快去通知管理员，bot已经废物了出的问题是:\n{err}")
        try: 
            for symbol in symbols:
                message += cal_symbols_avg_stooq(symbol[0],symbol[1:])
            bot.send_message(notifychat,message)
            bot.send_message(adminchat,f"{notifychat}向发送成功夕阳红:\n{message}")
        except Exception as err:
            bot.send_message(adminchat,f"今天完蛋了，stooq什么都不知道，快去通知管理员，bot已经废物了出的问题是:\n{err}")   

