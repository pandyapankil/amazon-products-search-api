# Use an official Python runtime as the base image
FROM python:3.10

# Create celeryuser
RUN useradd -ms /bin/bash celeryuser

# Set up environment variables
ENV DEBUG=false

# Install necessary dependencies
RUN apt-get update \
	&& apt-get install -y libnss3 xvfb gconf-service libasound2 libatk1.0-0 libc6 libcairo2 libcups2 \
	libdbus-1-3 libexpat1 libfontconfig1 libgbm1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 \
	libgtk-3-0 libnspr4 libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 \
	libxcomposite1 libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 \
	libxtst6 ca-certificates fonts-liberation libappindicator1 libnss3 lsb-release xdg-utils \
	&& apt-get autoclean \
	&& rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Create a virtual environment
RUN python3 -m venv /venv

# Activate the virtual environment
ENV PATH="/venv/bin:$PATH"

# Copy the requirements.txt file and install the dependencies
COPY backend/requirements.txt .
RUN pip install --upgrade pip \
	&& pip install --no-cache-dir -r requirements.txt

# Copy the entire project to the working directory
COPY backend /app
