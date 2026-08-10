FROM python:3.10-slim

# Install the stockfish engine
RUN apt-get update && apt-get install -y stockfish

WORKDIR /app

# Install your dependencies
COPY requirements.get .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your bot files
COPY . .

# Run your bot script
CMD ["python3", "main.py"]
