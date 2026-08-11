#!/usr/bin/env bash
set -o errexit

echo "--- Custom Build Script Started ---"

# 1. Install regular Python dependencies
pip install -r requirements.txt

# 2. Setup folders for the opening book and the engine
mkdir -p config/assets/books
mkdir -p bin

# 3. Download your opening book from GitHub Releases
echo "Downloading opening book..."
curl -L -o config/assets/books/gm2001.bin "https://github.com/GoogleHub67/Lichess-Inappropriate_BOT/releases/download/V1.0.0/gm2001.bin"

# 4. Download a precompiled Linux Ubuntu-64 bit Stockfish binary
echo "Downloading Linux Stockfish Engine..."
curl -L -o bin/stockfish "https://sourceforge.net/projects/stockfish.mirror/files/sf_16.1/stockfish-ubuntu-x86-64-avx2.tar"

# 5. Grant executable permissions to the Linux binary
chmod +x bin/stockfish

echo "--- Build Script Finished Successfully ---"
