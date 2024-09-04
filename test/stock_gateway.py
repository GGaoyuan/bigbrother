import apscheduler.events

"""
一、日常交易时间
上午交易时段：每周一至周五的上午9:30至11:30，共计2小时。这是股票市场的正式开盘时间，投资者可以在此期间内下单买卖股票。
下午交易时段：每周一至周五的下午13:00（即下午1点）至15:00（即下午3点），共计2小时。这是股票市场的下午交易时段，同样允许投资者进行股票的买卖。
二、集合竞价时间
在正式的交易时间之前和之后，还有集合竞价的时间段，用于确定开盘价和收盘价。

开盘集合竞价：上午9:15至9:25。在这个时间段内，市场会进行集合竞价，以确定开盘价。需要注意的是，9:15至9:20可以挂单和撤单，但9:20至9:25只能挂单不能撤单。9:25时，交易所会根据集合竞价的原则确定开盘价，并开始连续竞价。
尾盘集合竞价：下午14:57至15:00。这个时间段内可以挂单但不能撤单，此时的成交价格将决定股票当天的收盘价。需要注意的是，尾盘集合竞价可能仅在部分市场（如深圳市场）进行。
"""
import apscheduler.events
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, time
import inspect
import akshare as ak
import test.email as email

def schedule_listener(event):
    if event.exception:
        caller_frame = inspect.stack()[1]
        caller_method_name = caller_frame.function
        email.send(f"{caller_method_name}: {event.exception}")

def prepare_task():
    # 今日是否可以交易
    global tradable
    today = datetime.now().strftime('%Y-%m-%d')
    trade_date = ak.tool_trade_date_hist_sina()['trade_date'].values.astype(str)
    tradable = today in trade_date
    # email.send(f'Preparing task：tradable = {tradable}')
    if tradable:
        email.send('_prepare_task - 今日可交易')
    else:
        email.send('_prepare_task - 今日不可交易')



def mor_open_task():
    global tradable
    if tradable:
        email.send('mor_open_task')
    else:
        email.send('mor_open_task no')

def mor_close_task():
    global tradable
    if tradable:
        email.send('mor_close_task')
    else:
        email.send('mor_close_task no')

def aft_open_task():
    global tradable
    if tradable:
        email.send('aft_open_task')
    else:
        email.send('aft_open_task no')

def aft_close_task():
    global tradable
    tradable = False
    if tradable:
        email.send('aft_close_task')
    else:
        email.send('aft_close_task no')


prepare_time = time(hour=9, minute=10)
mor_open_time = time(hour=9, minute=30)
mor_close_time = time(hour=11, minute=0)
aft_open_time = time(hour=13, minute=0)
aft_close_time = time(hour=15, minute=0)
tradable = False
scheduler = BlockingScheduler()
scheduler.add_job(func=prepare_task,
                      trigger=CronTrigger(hour=prepare_time.hour, minute=prepare_time.minute))
scheduler.add_job(func=mor_open_task,
                      trigger=CronTrigger(hour=mor_open_time.hour, minute=mor_open_time.minute))
scheduler.add_job(func=mor_close_task,
                      trigger=CronTrigger(hour=mor_close_time.hour, minute=mor_close_time.minute))
scheduler.add_job(func=aft_open_task,
                      trigger=CronTrigger(hour=aft_open_time.hour, minute=aft_open_time.minute))
scheduler.add_job(func=aft_close_task,
                      trigger=CronTrigger(hour=aft_close_time.hour, minute=aft_close_time.minute))
# 监听器
scheduler.add_listener(schedule_listener,
                       apscheduler.events.EVENT_JOB_ERROR | apscheduler.events.EVENT_JOB_EXECUTED)
scheduler.start()

# 判断开启
current_time = datetime.now().time()
if prepare_time <= current_time <= aft_close_time:
    email.send('当前处于交易时间，开启失败。9~15点请不要开启脚本')
