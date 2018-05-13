import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from .trader import print_greetings

scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(print_greetings,
                  id='greetings',
                  name='test',
                  trigger='cron',
                  second='*/2',
                  )

atexit.register(lambda: scheduler.shutdown())
