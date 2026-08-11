#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status
set -o errexit

echo "--- Custom Build Script Started ---"

# 1. Install regular Python dependencies
pip install -r requirements.txt

# 2. Setup folders for the opening book and the engine
mkdir -p config/assets/books
mkdir -p bin

# 3. Download the opening book from your GitHub Releases asset
echo "Downloading opening book..."
curl -L -o config/assets/books/gm2001.bin "https://github.com"

# 4. Download a precompiled Linux-64 bit Stockfish binary
echo "Downloading Linux Stockfish Engine..."
curl -L -o bin/stockfish "https://github.com"

# 5. Make the Stockfish binary executable by the server
chmod +x bin/stockfish

echo "--- Build Script Finished Successfully ---"
