import uvicorn
from bs4 import BeautifulSoup
from core.config import settings
from fastapi import FastAPI, HTTPException, status
from pydantic import EmailStr
from scrap_script import scrap_page

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)


async def scrap(search_keywords, products_count):
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
			traverse_upto = products_count - count
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


@app.get("/search")
async def get_products(search_keywords: str, products_count: int = 10):
	if products_count > 1000:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="products_count must not be greater than 100")

	keywords_to_search = "+".join(search_keywords.split())
	result = await scrap(keywords_to_search, products_count)

	return result


# TODO: 1 separate endpoint which will take an email id from user if products_count is g.t. 20
# that will be handled using celery with redis broker in background and then result will be sent over email
# TODO: 1-1 print the response first over console
# TODO: 1-2 send to the email provided
# TODO: 2 start with the simplest DB to store the result against keyword; key-value store is a good choice
# TODO: 3 serve DB separately
# TODO: 4 containerize the app
# TODO: 5 add jwt auth to restrict usage to authenticated users
# TODO:
# TODO: 6 add kubernetess if time permits

if __name__ == "__main__":
	uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
