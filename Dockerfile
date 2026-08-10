FROM python:3.10-slim

# Install the stockfish engine
RUN apt-get update && apt-get install -y stockfish && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Force install gunicorn and flask for the web layer
RUN pip install --no-cache-dir flask gunicorn

# Copy all project files
COPY . .

# Run the web application using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
