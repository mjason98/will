FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends gcc && \
	pip install --no-cache-dir -r requirements.txt && \
    pip install "python-telegram-bot[job-queue]" && \
	pip install "lxml[html_clean]" && \
	apt-get purge -y --auto-remove gcc && \
	rm -rf /var/lib/apt/lists/*

# Copy bot code
COPY . .

# Run the bot
CMD ["python", "main.py"]