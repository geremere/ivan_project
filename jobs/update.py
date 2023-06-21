from apscheduler.schedulers.background import BackgroundScheduler

from jobs.jobs import daily, weekly, monthly


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(daily, 'interval', seconds=60 * 60 * 24)
    scheduler.add_job(weekly, 'interval', seconds=60 * 60 * 24 * 7)
    scheduler.add_job(monthly, 'interval', seconds=60 * 60 * 24 * 30)
    scheduler.start()
