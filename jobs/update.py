from apscheduler.schedulers.background import BackgroundScheduler

from jobs.jobs import daily, weekly, monthly, clear_black_list


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(daily, 'interval', seconds=60 * 60 * 24)
    scheduler.add_job(weekly, 'interval', seconds=60 * 60 * 24)
    scheduler.add_job(monthly, 'interval', seconds=60 * 60 * 24)
    scheduler.add_job(clear_black_list, 'interval', seconds=60 * 60 * 24)
    scheduler.start()
