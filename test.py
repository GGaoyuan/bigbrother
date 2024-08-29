import apscheduler.events
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
#
# from stock.stock_gateway import tradable
# 
# tradable = 1
# 
# def test():
#     global tradable
#     print(tradable)
# 
def prepare_task():
    global tradable
    tradable = True
    print('prepare_task')


def mor_open_task():
    global tradable
    if tradable:
        print('mor_open_task')
    else:
        print('mor_open_task no')

def mor_close_task():
    global tradable
    if tradable:
        print('mor_close_task')
    else:
        print('mor_close_task no')

def aft_open_task():
    global tradable
    if tradable:
        print('aft_open_task')
    else:
        print('aft_open_task no')

def aft_close_task():
    global tradable
    tradable = False
    if tradable:
        print('aft_close_task')
    else:
        print('aft_close_task no')


scheduler = BlockingScheduler()
scheduler.add_job(func=prepare_task,
                      trigger=CronTrigger(hour=22, minute=28))
scheduler.add_job(func=mor_open_task,
                      trigger=CronTrigger(hour=22, minute=29))
scheduler.add_job(func=mor_close_task,
                      trigger=CronTrigger(hour=22, minute=30))
scheduler.add_job(func=aft_open_task,
                      trigger=CronTrigger(hour=22, minute=31))
scheduler.add_job(func=aft_close_task,
                      trigger=CronTrigger(hour=22, minute=32))
scheduler.start()

#
#
# import apscheduler.events
# from apscheduler.schedulers.blocking import BlockingScheduler
# from apscheduler.triggers.cron import CronTrigger
# import akshare as ak
# from datetime import datetime, time
# import utils.email as email
# import inspect
# """
# 一、日常交易时间
# 上午交易时段：每周一至周五的上午9:30至11:30，共计2小时。这是股票市场的正式开盘时间，投资者可以在此期间内下单买卖股票。
# 下午交易时段：每周一至周五的下午13:00（即下午1点）至15:00（即下午3点），共计2小时。这是股票市场的下午交易时段，同样允许投资者进行股票的买卖。
# 二、集合竞价时间
# 在正式的交易时间之前和之后，还有集合竞价的时间段，用于确定开盘价和收盘价。
#
# 开盘集合竞价：上午9:15至9:25。在这个时间段内，市场会进行集合竞价，以确定开盘价。需要注意的是，9:15至9:20可以挂单和撤单，但9:20至9:25只能挂单不能撤单。9:25时，交易所会根据集合竞价的原则确定开盘价，并开始连续竞价。
# 尾盘集合竞价：下午14:57至15:00。这个时间段内可以挂单但不能撤单，此时的成交价格将决定股票当天的收盘价。需要注意的是，尾盘集合竞价可能仅在部分市场（如深圳市场）进行。
# """
#
#
# # def start_scheduler():
# #     print('start_scheduler')
# #     # 启动调度器
# #     scheduler.start()
#
# def schedule_listener(event):
#     if event.exception:
#         caller_frame = inspect.stack()[1]
#         caller_method_name = caller_frame.function
#         print(f"{caller_method_name}: {event.exception}")
#
# def prepare_task():
#     # 今日是否可以交易
#     global tradable
#     today = datetime.now().strftime('%Y-%m-%d')
#     trade_date = ak.tool_trade_date_hist_sina()['trade_date'].values.astype(str)
#     tradable = today in trade_date
#     print(f'Preparing task：tradable = {tradable}')
#     if tradable:
#         print('_prepare_task - 今日可交易')
#     else:
#         print('_prepare_task - 今日不可交易')
#
# def mor_open_task():
#     global tradable
#     if tradable:
#         print('_mor_open_task')
#     else:
#         print('mor_close_task no')
#
# def mor_close_task():
#     global tradable
#     if tradable:
#         print('_mor_close_task')
#     else:
#         print('mor_close_task no')
#
# def aft_open_task():
#     global tradable
#     if tradable:
#         print('_aft_open_task')
#     else:
#         print('_aft_open_task no')
#
# def aft_close_task():
#     global tradable
#     tradable = False
#     if tradable:
#         print('_aft_close_task')
#     else:
#         print('aft_close_task no')
#
#
#
#
#
# scheduler = BlockingScheduler()
# tradable = False
# prepare_time = time(hour=22, minute=14)
# mor_open_time = time(hour=22, minute=15)
# mor_close_time = time(hour=22, minute=16)
# aft_open_time = time(hour=22, minute=17)
# aft_close_time = time(hour=22, minute=18)
#
# current_time = datetime.now().time()
# if prepare_time <= current_time <= aft_close_time:
#     print('当前处于交易时间，开启失败。9~15点请不要开启脚本')
# else:
#     print('开启scheduler')
#
#     # 早市准备
# # global scheduler
# scheduler.add_job(func=prepare_task,
#                   trigger=CronTrigger(hour=22, minute=23),
#                   id='prepare_task')
# # 早市开始和结束
# scheduler.add_job(func=mor_open_task,
#                   trigger=CronTrigger(hour=22, minute=24),
#                   id='mor_open_task')
# scheduler.add_job(func=mor_close_task,
#                   trigger=CronTrigger(hour=22, minute=25),
#                   id='mor_close_task')
# # 午市开始和结束
# scheduler.add_job(func=aft_open_task,
#                   trigger=CronTrigger(hour=22, minute=26),
#                   id='aft_open_task')
# scheduler.add_job(func=aft_close_task,
#                   trigger=CronTrigger(hour=22, minute=27),
#                   id='aft_close_task')
# # 监听器
# # scheduler.add_listener(schedule_listener,
# #                        apscheduler.events.EVENT_JOB_ERROR | apscheduler.events.EVENT_JOB_EXECUTED)
# scheduler.start()
#




