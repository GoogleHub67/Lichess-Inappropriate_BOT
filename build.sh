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
if curl -L -o assets/books/gm2001.bin "https://github.com/GoogleHub67/Lichess-Inappropriate_BOT/releases/download/V1.0.0/gm2001.bin"; then
    echo "✓ Opening book downloaded successfully"
    ls -lh assets/books/gm2001.bin
else
    echo "✗ Failed to download opening book"
    exit 1
fi

# 4. Download a precompiled Linux Ubuntu-64 bit Stockfish binary
echo "Downloading Linux Stockfish Engine..."
if curl -L -o bin/stockfish.tar "https://sourceforge.net/projects/stockfish.mirror/files/sf_16.1/stockfish-ubuntu-x86-64-avx2.tar"; then
    echo "✓ Stockfish archive downloaded"
    
    # Extract the tar file
    echo "Extracting Stockfish..."
    cd bin
    tar -xf stockfish.tar
    
    # Find and move the stockfish binary to bin/stockfish
    if [ -f "stockfish-ubuntu-x86-64-avx2/stockfish" ]; then
        mv stockfish-ubuntu-x86-64-avx2/stockfish ./
        rm -rf stockfish-ubuntu-x86-64-avx2
        echo "✓ Stockfish extracted successfully"
    else
        echo "✗ Could not find stockfish binary in archive"
        exit 1
    fi
    
    cd ..
    
    # Grant executable permissions to the Linux binary
    chmod +x bin/stockfish
    ls -lh bin/stockfish
else
    echo "✗ Failed to download Stockfish"
    exit 1
fi

echo "--- Build Script Finished Successfully ---"
