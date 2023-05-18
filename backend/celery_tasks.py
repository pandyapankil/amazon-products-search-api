from prelude import *

__redis_url = f'redis://{c.REDIS_HOST}:{c.REDIS_PORT}/0'
celery = Celery("tasks", broker=f"{__redis_url}", backend=__redis_url)
celery.conf.task_serializer = 'pickle'
celery.conf.result_serializer = 'pickle'
celery.conf.accept_content = {'pickle'}

celery.conf.task_acks_late = True
celery.conf.worker_prefetch_multiplier = 1
celery.conf.task_queue_max_priority = 2


class CeleryTaskBase(celery.Task):
	'''
	Override on_failure to post errors on log
	To use this:
	use @celery.task(base=CeleryTaskBase) decorator instead of @celery.task
	'''

	def on_failure(self, exc, task_id, args, kwargs, einfo):
		logger.info(f'Celery Task {args} {kwargs}', einfo.traceback)


@celery.task(base=CeleryTaskBase)
def scrap_and_send_email(email: EmailStr, **kwargs):
	response = requests.get("http://scraper:8080/scrap", params=kwargs)
	resp = response.text
	result = json.loads(resp)
	search_keywords = kwargs["search_keywords"]
	redis.delete(search_keywords)
	redis.rpush(search_keywords, json.dumps(result))
	redis.expire(search_keywords, 4 * 24 * 60 * 60)
	logger.info("Data stored in Redis successfully.") # type: ignore
