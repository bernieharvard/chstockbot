import getopt,sys,config,os
from numpy.lib.function_base import append
from numpy import cos, e, mafromtxt, result_type
from requests.api import get
from requests.sessions import extract_cookies_to_jar
import time, datetime
from telegram import Bot
from pandas_datareader._utils import RemoteDataError
from requests.exceptions import ConnectionError
from stockutil import stooq, wikipedia



def get_week_num(year, month, day):
    """
    获取当前日期是本月的第几周
    """
    start = int(datetime.date(year, month, 1).strftime("%W"))
    end = int(datetime.date(year, month, day).strftime("%W"))
    week_num = end - start + 1
    # 判断是否是包含周三的第二周
    # if datetime.date(year, month, 1).weekday() < 3: 
    #     week_num = week_num
    # else:
    #     result = week_num -1
    return week_num

def get_price_data(symbol,start = datetime.date(2021,1,1), end = datetime.date.today()):
    """
    得到某ticker指定时间段特定的数据。
    特定时间为每周三和每月第二周的周三。

    Parameters
    ----------
    symbol : 股票代码 
    start : 开始的日期，默认2021-01-01
    end : 结束日期，默认程序运行当天
    """
    ticker_price_data = {}
    if start < end:
        try:
            ticker_file = stooq.search_file(symbol.lower().replace(".","-") + ".us.txt",os.path.expanduser("~/Downloads/data"))
            df = stooq.read_stooq_file(path=ticker_file[0])["Adj Close"]   
            df_w = []
            df_m = []
            err_msg =""
            for date in df.index:
                if date > start and date < end:
                    if date.weekday() == 3:
                        df_w.append(df[date])
                        ticker_price_data['Weekly Price'] = [df_w, err_msg]
                        continue
                    if get_week_num(date.year,date.month,date.day) == 2:
                        df_m.append(df[date])
                        ticker_price_data['Monthly Price'] = [df_m, err_msg]
        except Exception as e:
            ticker_price_data['Error'] = [f"提取{symbol.upper()}数据出错了。\nerror message: {e}\n"]
    else:
        ticker_price_data['Date Error'] = ["输入的日期可能有误，请检查。"]

    return ticker_price_data
    
def get_invest_profit(ticker_price, start = datetime.date(2021,1,1), end = datetime.date.today()):
    """
    计算某ticker指定时间段的利润率。

    Parameters
    ----------
    ticker_price : 每个定投日的收盘价格列表。 
    start : 开始的日期，默认2021-01-01
    end : 结束日期，默认程序运行当天
    """
    price_list = ticker_price[0]
    err_msg = ticker_price[1]
    times = len(price_list)

    #每周投入金额一样
    stock_num = 0
    for i in range (times):    
        stock_num += 100/price_list[i]
    cost = 100 * times
    cur_value = stock_num * price_list[times-1]
    profit = cur_value - cost
    
    #每周买入股数一样
    # cost = 0
    # for i in range (times):    
    #     cost += 1 * price_list[i]
    # stock_num = 1 * times
    # cur_value = stock_num * price_list[times-1]
    # profit = cur_value - cost

    return [f"{(profit/cost)*100:.2f}%", err_msg, f"{cost:.2f}", f"{cur_value:.2f}"]

def sendmsg(bot,chatid,msg,debug=True):
    if debug:
        print(f"{chatid}\n{msg}")
    else:
        bot.send_message(chatid,msg)

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
    symbols = CONFIG['xyhticker']
    notifychat = CONFIG['xyhchat']
    adminchat = CONFIG['xyhlog']
    debug = CONFIG['DEBUG']
    ds = CONFIG['xyhsource']
    tickers = CONFIG['mmtticker']
    #tickers = ['qqq','spy']

    start = datetime.date(2021,1,1)
    d = datetime.date.today()  
    d = datetime.date(2021,5,1)

    mmt_week = "如果你每周定投，哪么今天是投 #小毛毛 的日子啦，今天是周三 请向小🐷🐷中塞入你虔诚的🪙吧～"
    mmt_month = "如果你每月定投，哪么今天是投 #大毛毛 的日子啦，今天是本月第二周的周三 请向小🐷🐷中塞入你虔诚的💰吧～ \n 如果你每周定投，今天依然是投 #小毛毛 的日子 放入🪙，哪么今天照常放入虔诚的🪙吧～"

    if get_week_num(d.year,d.month,d.day) == 2:
        sendmsg(bot,notifychat,mmt_month,debug)
    else:
        sendmsg(bot,notifychat,mmt_week,debug)


    weekly_profit_msg = ""
    weekly_err_msg = ""

    for symbol in tickers:
        if 'Weekly Price' in get_price_data(symbol,start = start,end = d):
            ticker_weekly = get_price_data(symbol,start = start,end = d)['Weekly Price']
            profit_rate, err_msg, cost, cur_value = get_invest_profit(ticker_weekly, start, end=d)
            weekly_profit_msg += f"如果从{start}开始，每周三定投{symbol.upper()} 100元，截止到{d}，累计投入{cost}，市值为{cur_value}，利润率为 {profit_rate}\n"
        if 'Error' in get_price_data(symbol,start = start,end = d):
            err_msg = get_price_data(symbol,start = start,end = d)['Error']
            weekly_err_msg += f"{err_msg}"
        elif 'Data Error' in get_price_data(symbol,start = start,end = d):
            weekly_err_msg = f"{get_price_data(symbol,start = start,end = d)['Date Error']}"
    if weekly_profit_msg:
        sendmsg(bot,notifychat, weekly_profit_msg,debug)
    if weekly_err_msg:
        sendmsg(bot, adminchat, weekly_err_msg, debug)


    monthly_profit_msg = ""
    monthly_err_msg = ""

    for symbol in tickers:
        if 'Monthly Price' in get_price_data(symbol,start = start,end = d):
            ticker_monthly = get_price_data(symbol,start = start,end = d)['Monthly Price']
            profit_rate, err_msg, cost, cur_value = get_invest_profit(ticker_monthly, start = start, end = d)
            monthly_profit_msg += f"如果从{start}开始，每月第二周的周三定投{symbol.upper()} 100元，截止到{d}，累计投入{cost}，市值为{cur_value}，利润率为 {profit_rate}\n"
        if 'Error' in get_price_data(symbol,start = start,end = d):
            err_msg = get_price_data(symbol,start = start,end = d)['Error']
            monthly_err_msg += f"{err_msg}"
        elif 'Data Error' in get_price_data(symbol,start = start,end = d):
            Monthly_err_msg = f"{get_price_data(symbol,start = start,end = d)['Date Error']}"
    if monthly_profit_msg:
        sendmsg(bot,notifychat, monthly_profit_msg,debug)
    if monthly_err_msg:
        sendmsg(bot, adminchat, monthly_err_msg, debug)
