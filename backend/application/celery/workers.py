from celery import Celery
from flask import current_app as app

celery = Celery('MyKanban Backend Jobs')

class KanbanTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)