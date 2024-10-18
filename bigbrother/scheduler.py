from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = BackgroundScheduler()

def run_daily(hours: int, seconds: int):
    scheduler.start()

def run_seconds(hours: int, seconds: int):
    scheduler.start()