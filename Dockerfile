FROM python:3.10-slim

# Install the stockfish engine and clear out package manager cache
RUN apt-get update && apt-get install -y stockfish && rm -rf /var/lib/apt/lists/*

# Force give execution permission flags to the Stockfish binary
RUN chmod +x /usr/games/stockfish

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files from GitHub
COPY . .

# Run via a standard threaded worker setup to keep python-chess subprocess communication stable
CMD ["gunicorn", "--workers", "1", "--threads", "4", "--bind", "0.0.0.0:10000", "app:app"]
