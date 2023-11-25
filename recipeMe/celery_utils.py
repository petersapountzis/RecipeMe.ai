from celery import Celery

def make_celery(app_name, broker_url):
    celery = Celery(app_name, broker=broker_url)
    celery.conf.update(
        # Add any additional configuration here
    )
    return celery