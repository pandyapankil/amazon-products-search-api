import pyppeteer
import pyppeteer.connection

#patch to stop default ping timeout after 20 seconds.
original_method = pyppeteer.connection.websockets.connect


def new_method(*args, **kwargs):
	kwargs['ping_interval'] = None
	kwargs['ping_timeout'] = None
	return original_method(*args, **kwargs)


pyppeteer.connection.websockets.connect = new_method


def get_patched_pyppeteer():
	return pyppeteer
