from celery.utils.log import get_task_logger
from celery.schedules import crontab
from celery.task import periodic_task
from django.utils import timezone

from stories.models import Story
logger = get_task_logger(__name__)


@periodic_task(run_every=(crontab(minute='*/2')), name="some_task", ignore_result=True)
def delete_expired_stories():
    stories = Story.objects.all()
    for story in stories:
        if story.expiration_date < timezone.now():
            story.delete()

    return "completed deleting story at {}".format(timezone.now())
