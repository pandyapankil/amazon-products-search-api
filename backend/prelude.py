import json
import logging

import aiohttp
import constants as c
import requests
import uvicorn
from celery import Celery
from fastapi import FastAPI, HTTPException, status
from pydantic import EmailStr
from redis import Redis

redis = Redis(host=c.REDIS_HOST, port=c.REDIS_PORT, db=0) # type: ignore

logging.basicConfig(level=logging.INFO) # Add logging configuration
logger = logging.getLogger(__name__)
