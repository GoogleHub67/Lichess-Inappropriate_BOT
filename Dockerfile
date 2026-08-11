FROM python:3.10-slim

# Install the stockfish engine and clean cache
RUN apt-get update && apt-get install -y stockfish && rm -rf /var/lib/apt/lists/*

# Grant direct execution permissions to the binary file
RUN chmod +x /usr/games/stockfish

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Run the web application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
