# Use an appropriate base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy all project files from GitHub
COPY . .

# Set environment variable for Stockfish path
ENV STOCKFISH_PATH=/app/tests/assets/stockfish/linux/stockfish

# Force give execution permission flags to the Stockfish binary
RUN chmod +x "$STOCKFISH_PATH"

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Check the architecture and log it
RUN uname -m >> architecture.log

# Run the diagnostic script to verify Stockfish setup
RUN ["python", "error.py"]

# Command to run the web application using Gunicorn with an asynchronous gevent worker class
CMD ["gunicorn", "--worker-class", "gevent", "--workers", "1", "--bind", "0.0.0.0:10000", "app:app"]
