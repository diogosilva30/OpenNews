from celery import shared_task
from .models import NewsFactory


@shared_task
def enqueue_url_search_job(factory_cls: NewsFactory, **job_kwargs):
    return factory_cls.from_url_search(**job_kwargs)
