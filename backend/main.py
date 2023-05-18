from celery_tasks import scrap_and_send_email
from core.config import settings
from prelude import *

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)


async def perform_pyppeteer_operation(**kwargs):
	async with aiohttp.ClientSession() as session:
		async with session.get("http://scraper:8080/scrap", params=kwargs) as response:
			resp = await response.text()
			data = json.loads(resp)
			return data


def get_result_from_cache(search_keywords: str, products_count: int):
	if redis.exists(search_keywords):
		result = json.loads(redis.lrange(search_keywords, 0, -1)[0])
		if products_count <= len(result):
			return result[:products_count]
	return None


@app.get("/search")
async def get_products_wo_email(search_keywords: str, products_count: int = 10):
	"""
	Return Amazon products data

	Parameters:
	- search_keywords(str): Keywords to search on Amazon page.
	- products_count(int): Number of products to get from the Amazon page.
	"""
	if products_count > 1000:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="products_count must not be greater than 100")

	keywords_to_search = "+".join(search_keywords.split())
	cache_result = get_result_from_cache(keywords_to_search, products_count)
	if cache_result is not None:
		return cache_result

	result = await perform_pyppeteer_operation(search_keywords=keywords_to_search, products_count=products_count)
	return result


@app.get("/search_with_email")
async def get_products_with_email(email: EmailStr, search_keywords: str, products_count: int = 10):
	"""
	Get Amazon products data over email

	Parameters:
	- email(EmailStr): Email to get Amazon data on.
	- search_keywords(str): Keywords to search on Amazon page.
	- products_count(int): Number of products to get from the Amazon page.
	"""
	if products_count <= 20:
		raise HTTPException(
			status_code=status.HTTP_400_BAD_REQUEST, detail="Please use /search endpoint for products_count <= 20"
		)
	if email is None:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email address can not be empty")

	keywords_to_search = "+".join(search_keywords.split())
	cache_result = get_result_from_cache(keywords_to_search, products_count)
	if cache_result is not None:
		return cache_result

	scrap_and_send_email.delay(
		email=email,
		search_keywords=keywords_to_search,
		products_count=products_count,
	)

	return dict(message="Result will be sent over email.")

#TODO: 1 get it working with task queue
# TODO: 2 containerize the app
# TODO: 3 add jwt auth to restrict usage to authenticated users

if __name__ == "__main__":
	uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=c.DEBUG)
