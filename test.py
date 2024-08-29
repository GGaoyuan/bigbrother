import apscheduler.events
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, time
import inspect
import akshare as ak
import utils.email as email

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
    email.send(f'Preparing task：tradable = {tradable}')
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


prepare_time = time(hour=22, minute=49)
mor_open_time = time(hour=22, minute=50)
mor_close_time = time(hour=22, minute=51)
aft_open_time = time(hour=22, minute=52)
aft_close_time = time(hour=22, minute=53)
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
