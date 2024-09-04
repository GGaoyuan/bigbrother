# import apscheduler.events
# from apscheduler.schedulers.blocking import BlockingScheduler
# from apscheduler.triggers.cron import CronTrigger
# from datetime import datetime, time
# import inspect
# import akshare as ak
#
#
#
# class TimeSchedule(object):
#     def __init__(self):
#         hour = 14
#         minute = 33
#         jobs = (
#             {'time': time(hour, minute, 10), 'func': self.prepare_task},
#             {'time': time(hour, minute, 15), 'func': self.mor_open_task},
#             {'time': time(hour, minute, 20), 'func': self.mor_close_task},
#             {'time': time(hour, minute, 25), 'func': self.aft_open_task},
#             {'time': time(hour, minute, 30), 'func': self.aft_close_task},
#         )
#         current_time = datetime.now().time()
#         if jobs[1].get('time') <= current_time <= jobs[len(jobs) - 1].get('time'):
#             print('当前处于交易时间，交易可能会混乱，赶紧关掉。9~15点请不要开启脚本')
#
#         self.tradable = False
#         self.tradabling = False
#         self.scheduler = BlockingScheduler()
#         for job in jobs:
#             job_time = job['time']
#             self.scheduler.add_job(func=job['func'], trigger=CronTrigger(hour=job_time.hour, minute=job_time.minute, second=job_time.second))
#         # 监听器
#         self.scheduler.add_listener(schedule_listener,
#                                     apscheduler.events.EVENT_JOB_ERROR | apscheduler.events.EVENT_JOB_EXECUTED)
#         self.scheduler.start()
#
#
#
#     def __del__(self):
#         print('StockSchedule __del__')
#
#     def prepare_task(self):
#         # 今日是否可以交易
#         today = datetime.now().strftime('%Y-%m-%d')
#         trade_date = ak.tool_trade_date_hist_sina()['trade_date'].values.astype(str)
#         self.tradable = today in trade_date
#         if self.tradable:
#             for strategy in self.strategies:
#                 strategy.prepare_trading()
#         else:
#             print('_prepare_task - 今日不可交易')
#
#     def mor_open_task(self):
#         if self.tradable:
#             for strategy in self.strategies:
#                 strategy.morning_market_open()
#         else:
#             print('mor_open_task untradable')
#
#     def mor_close_task(self):
#         if self.tradable:
#             for strategy in self.strategies:
#                 strategy.morning_market_close()
#         else:
#             print('mor_close_task untradable')
#
#     def aft_open_task(self):
#         if self.tradable:
#             for strategy in self.strategies:
#                 strategy.afternoon_market_open()
#         else:
#             print('aft_open_task untradable')
#
#     def aft_close_task(self):
#         if self.tradable:
#             for strategy in self.strategies:
#                 strategy.afternoon_market_close()
#         else:
#             print('aft_close_task untradable')
#         self.tradable = False