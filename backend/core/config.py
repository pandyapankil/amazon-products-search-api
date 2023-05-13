from typing import List, Optional


class Settings:
	PROJECT_NAME: str = "Amazon Products Fetch"
	PROJECT_VERSION: str = "1.0.0"
	API_V1_STR: str = "/api/v1"
	BACKEND_CORS_ORIGINS: Optional[List[str]] = []


settings = Settings()
