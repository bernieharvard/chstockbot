import sendxyh
import datetime

msg = sendxyh.cal_symbols_avg(['yahoo','stooq'],"aaaaabbbb",[10,50],end=datetime.date(2021,6,18))
print(msg)