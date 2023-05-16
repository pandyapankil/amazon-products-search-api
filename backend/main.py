import json
import logging
import os

import constants as c
import uvicorn
from bs4 import BeautifulSoup
# from celery import Celery
from core.config import settings
from fastapi import BackgroundTasks, FastAPI, HTTPException, status
from pydantic import EmailStr
from redis import Redis
from scrap_script import scrap_page

# import subprocess

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)

# __redis_url = f'redis://{c.REDIS_HOST}:{c.REDIS_PORT}/0'
# celery_app = Celery(app.title, broker=f"{__redis_url}")
redis = Redis(host=c.REDIS_HOST, port=c.REDIS_PORT, db=0) # type: ignore

logging.basicConfig(level=logging.INFO) # Add logging configuration
logger = logging.getLogger(__name__)


async def scrap(search_keywords: str, products_count: int):
	base_url = "https://www.amazon.in"
	output = []
	count = 0
	page_no = 1
	while count < products_count:
		html_response = await scrap_page(f"{base_url}/s?k={search_keywords}&page={page_no}")
		soup = BeautifulSoup(html_response, "html.parser")

		# Extract the search result items from the HTML content
		search_results = soup.find_all('div', {'data-component-type': 's-search-result'})
		if products_count - count > len(search_results):
			traverse_upto = -1
			count += len(search_results)
		else:
			traverse_upto = products_count - count + 1
			count = products_count

		# Loop through the search result items and extract product details
		for result in search_results[:traverse_upto]:
			# Extract the product name
			product_name = result.find('h2', {'class': 'a-size-mini a-spacing-none a-color-base s-line-clamp-2'}).text.strip()
			print('Product Name:', product_name)

			# Extract the product image URL
			product_image = result.find('img', {'class': 's-image'})['src']
			print('Product Image URL:', product_image)

			# Extract the product price
			product_price = result.find('span', {'class': 'a-offscreen'}).text.strip()
			print('Product Price:', product_price)

			# Extract the product rating
			product_rating_tag = result.find('span', {'class': 'a-icon-alt'})
			if product_rating_tag is None:
				product_rating = None
				print('Product Rating: N/A')
			else:
				product_rating = product_rating_tag.text.strip()
				print('Product Rating:', product_rating)

			# Extract the product URL
			product_relative_url = result.find(
				'a', {'class': 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'}
			)['href']
			product_url = f"{base_url}{product_relative_url}"
			print('Product URL:', product_url)

			print('-' * 50)

			output.append(
				dict(
					product_name=product_name,
					product_image=product_image,
					product_price=product_price,
					product_rating=product_rating,
					product_url=product_url,
				)
			)

		page_no += 1

	return output


# @celery_app.task
async def scrap_and_send_email(search_keywords: str, products_count: int, email: EmailStr):
	result = await scrap(search_keywords, products_count)
	redis.delete(search_keywords)
	redis.rpush(search_keywords, json.dumps(result))
	redis.expire(search_keywords, 4 * 24 * 60 * 60)
	logger.info("Data stored in Redis successfully.") # type: ignore


@app.get("/search")
async def get_products_wo_email(search_keywords: str, products_count: int = 10):
	if products_count > 1000:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="products_count must not be greater than 100")

	keywords_to_search = "+".join(search_keywords.split())
	result = await scrap(keywords_to_search, products_count)
	return result


@app.get("/search_with_email")
async def get_products_with_email(
	email: EmailStr, search_keywords: str, background_tasks: BackgroundTasks, products_count: int = 10
):
	if email is None:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email address can not be empty")

	keywords_to_search = "+".join(search_keywords.split())
	if redis.exists(keywords_to_search):
		result = json.loads(redis.lrange(keywords_to_search, 0, -1)[0])
		print(len(result))
		if products_count <= len(result):
			return result[:products_count]

	background_tasks.add_task(
		scrap_and_send_email,
		search_keywords=keywords_to_search,
		products_count=products_count,
		email=email,
	)

	# params = dict(
	# 	search_keywords=keywords_to_search,
	# 	products_count=products_count,
	# 	email=email,
	# )
	# background_tasks.add_task(scrap_and_send_email.apply_async, kwargs=params)

	return dict(message="Result will be sent over email.")


# def start_celery_worker():
# 	subprocess.Popen([
# 		"celery",
# 		"-A",
# 		"main.celery_app",
# 		"worker",
# 		"--loglevel=info",
# 		"-P",
# 		"threads",
# 		"-c",
# 		"4", # Adjust the concurrency value as needed
# 	])

# @app.on_event("startup")
# async def on_start_event():
# 	start_celery_worker()

#TODO: 1 get it working with task queue
# TODO: 2 containerize the app
# TODO: 3 add jwt auth to restrict usage to authenticated users

if __name__ == "__main__":
	uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
