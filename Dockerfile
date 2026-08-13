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

# 🟢 THE REAL FIXED COMMAND FOR THIS APP.PY ARCHITECTURE:
# We switch Gunicorn's worker class to "gthread" so it natively supports 
# your background thread engine loop instead of throwing an exit code 3!
CMD ["gunicorn", "--workers", "1", "--worker-class", "gthread", "--threads", "4", "--bind", "0.0.0.0:10000", "app:app"]
