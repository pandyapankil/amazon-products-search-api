import pyppeteer_patch

#patch to make ping timeout to be 30s instead of infinite.
pyppeteer = pyppeteer_patch.get_patched_pyppeteer()


async def scrap_page(url):
	browser = await pyppeteer.launch(
		headless=False,
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
		],
	)
	page = await browser.newPage()
	await page.setUserAgent(
		'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3542.0 Safari/537.36'
	)
	await page.goto(url)
	html = await page.content()
	await browser.close()
	return html
