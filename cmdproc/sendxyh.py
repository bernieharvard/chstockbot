import pandas as pd
import pandas_datareader as pdr
import datetime
from telegram import Update, ForceReply, bot, botcommand
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import numpy as ny
from pandas import DataFrame

def sendxyh_command(update: Update, context:CallbackContext) -> None:
  
    start = datetime.date.today() - datetime.timedelta(days=365)
    end = datetime.date.today()

    symbol = 'spy'
    df = pdr.get_data_yahoo(symbol.upper(),start=start,end=end)
    print(df)

    
    dfma13 = pd.Series(df.tail(13), pd.date_range(end=end,freq='D',periods=13))
    ma13 = sum(dfma13.ix[0:13,'Close'])/13
    dfma50 = pd.Series(df.tail(50), pd.date_range(end=end,freq='D',periods=50))
    ma50 = sum(dfma50.ix[0:50,'Close'])/50
    dfma200 = pd.Series(df.tail(200), pd.date_range(end=end,freq='D',periods=200))
    ma200 = sum(dfma200.ix[0:200,'Close'])/200
    last_row = df.tail(1)
    high = last_row.iat[0,0]
    low = last_row.iat[0,1]
    close = last_row.iat[0,3]

    rainbowId = -1001409640737
    bot_reply =f"""
当日天相
{symbol}价格：{close}({low}-{high})
13周期均价：{ma13}
50周期均价：{ma50}
200周期均价：{ma200}


福如东海长流水，
寿比南山不老松！
"""
    bot.send_message(rainbowId,bot_reply)

def add_dispatcher(dp):
    dp.add_handler(CommandHandler("sendxyh", sendxyh_command))
    return []