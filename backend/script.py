import asyncio

import pyppeteer_patch
from bs4 import BeautifulSoup

#patch to make ping timeout to be 30s instead of infinite.
pyppeteer = pyppeteer_patch.get_patched_pyppeteer()


async def scrap_page(url):
	browser = await pyppeteer.launch(
		headless=True,
		args=[
			'--start-maximized',
			'--no-sandbox',
			'--disable-setuid-sandbox',
			'--disable-dev-shm-usage',
			'--disable-accelerated-2d-canvas',
			'--no-first-run',
			'--no-zygote',
			'--ignore-certificate-errors',
			'--single-process',
			'--disable-gpu',
		]
	)
	page = await browser.newPage()
	await page.goto(url)
	html = await page.content()
	await browser.close()
	return html


async def main():
	base_url = "https://www.amazon.in"
	search_keywords = "laptop"
	page_no = 3
	page_no = 1 if page_no is None else page_no
	html_response = await scrap_page(f"{base_url}/s?k={search_keywords}&page={page_no}")
	soup = BeautifulSoup(html_response, "html.parser")

	# Extract the search result items from the HTML content
	search_results = soup.find_all('div', {'data-component-type': 's-search-result'})

	# Loop through the search result items and extract product details
	for result in search_results:
		# Extract the product name
		product_name = result.find('h2', {'class': 'a-size-mini a-spacing-none a-color-base s-line-clamp-2'}).text.strip()
		print('Product Name:', product_name)

		# Extract the product image URL
		# product_image_tag = result.find('img', {'class': 's-image'})
		# print(product_image_tag)
		product_image = result.find('img', {'class': 's-image'})['src']
		print('Product Image URL:', product_image)

		# Extract the product price
		product_price = result.find('span', {'class': 'a-offscreen'}).text.strip()
		print('Product Price:', product_price)

		# Extract the product rating
		product_rating_tag = result.find('span', {'class': 'a-icon-alt'})
		if product_rating_tag is None:
			print('Product Rating: N/A')
		else:
			product_rating = product_rating_tag.text.strip()
			print('Product Rating:', product_rating)

		# Extract the product URL
		product_url = result.find(
			'a', {'class': 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'}
		)['href']
		print('Product URL:', f"{base_url}{product_url}")

		print('-' * 50)


asyncio.run(main())
