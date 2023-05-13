import uvicorn
from core.config import settings
from fastapi import FastAPI

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)


@app.get("/")
def hello_api():
	return dict(msg="Hello API")


if __name__ == "__main__":
	uvicorn.run(app, host="0.0.0.0", port=8000)
