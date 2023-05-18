from bs4 import BeautifulSoup
from core.config import scraper_settings
from prelude import *
from scrap_script import scrap_page

app = FastAPI(title=scraper_settings.PROJECT_NAME, version=scraper_settings.PROJECT_VERSION)


@app.get("/scrap")
async def scrap(search_keywords: str, products_count: int):
	base_url = "https://www.amazon.in"
	output = []
	count = 0
	page_no = 1
	while count < products_count:
		html_response = await scrap_page(f"{base_url}/s?k={search_keywords}&page={page_no}")
		soup = BeautifulSoup(html_response, "html.parser")

		# Extract the search result items from the HTML content
		data_component_search_results = soup.find_all('div', {'data-component-type': 's-search-result'})
		if data_component_search_results == []:
			search_results = soup.find_all('div', {'class': 'a-section a-spacing-base'})
		else:
			search_results = data_component_search_results

		# Loop through the search result items and extract product details
		for result in search_results:
			# Extract the product name
			if search_results == data_component_search_results:
				product_name_tag = result.find('h2', {'class': 'a-size-mini a-spacing-none a-color-base s-line-clamp-2'})
			else:
				product_name_tag = result.find('h2', {'class': 'a-size-mini a-spacing-none a-color-base s-line-clamp-4'})
			if product_name_tag is None:
				print("product is None")
				continue
			product_name = product_name_tag.text.strip()
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

			count += 1
			if count == products_count:
				break

		page_no += 1

	return output


if __name__ == "__main__":
	uvicorn.run(app="scrap_main:app", host="0.0.0.0", port=8080, reload=c.DEBUG)
