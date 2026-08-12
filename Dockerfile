# Use an appropriate base image
FROM python:3.9-slim

# Install necessary dependencies
RUN apt-get update && \
    apt-get install -y wget tar libc6-dev

# Set the working directory
WORKDIR /app

# Copy the project files to the working directory
COPY . /app

# Set environment variable for Stockfish path
ENV STOCKFISH_PATH=/app/stockfish

# Check the architecture and log it
RUN uname -m >> architecture.log

# Download Stockfish from GitHub releases and extract it
RUN wget -O stockfish.tar --no-check-certificate https://github.com/GoogleHub67/Lichess-Inappropriate_BOT/releases/download/V1.0.0/stockfish-ubuntu-x86-64-avx2.tar && \
    echo "Downloaded stockfish.tar" && \
    mkdir -p stockfish_dir && \
    tar -xvf stockfish.tar -C stockfish_dir && \
    echo "Extracted stockfish.tar contents" && \
    ls -l stockfish_dir && \
    mv stockfish_dir/stockfish* /app/stockfish && \
    echo "Moved stockfish to /app" && \
    rm -rf stockfish_dir stockfish.tar && \
    echo "Cleaned up files" && \
    chmod +x stockfish && \
    echo "Set executable permissions for /app/stockfish"

# Verify if the Stockfish binary exists
RUN if [ ! -f "$STOCKFISH_PATH" ]; then echo "Stockfish binary not found at $STOCKFISH_PATH"; exit 1; fi

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port if needed (if your bot runs a web server)
EXPOSE 5000

# Command to run the diagnostic script
CMD ["python", "error.py"]
