# Inappropriate_BOT - Adaptive Chess Partner

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Lichess](https://img.shields.io/badge/Lichess-Bot-brown)

A Lichess bot that dynamically adapts its playing strength to match your live 
skill level using centipawn loss analysis. The harder you play, the harder it 
plays back. Supports all Lichess variants with Fairy-Stockfish.

Built by Aarav Patel.

NOTE: Based on https://github.com/lichess-bot-devs/lichess-bot (AGPL License)

---

## How it works
```
Game starts
    |
    v
Bot plays at default ELO (1200)
    |
    v
Tracks your centipawn loss per move
    |   -> rolling average CPL
    |
    v
Maps avg CPL -> Stockfish ELO
    |   CPL <= 15  -> ELO 2200 (master)
    |   CPL <= 25  -> ELO 2000 (expert)
    |   CPL <= 40  -> ELO 1800 (strong club)
    |   CPL <= 60  -> ELO 1600 (intermediate)
    |   CPL <= 90  -> ELO 1400 (casual)
    |   CPL <= 130 -> ELO 1200 (beginner)
    |   CPL > 130  -> ELO 1000 (newcomer)
    v
Plays at that ELO for the rest of the game
```

---

## Features
- Fully adaptive strength based on live CPL
- Supports all Lichess variants (Fairy-Stockfish for variants)
- Smart draw handling (accepts when losing, declines when winning)
- Auto-resigns when mated in 3 or less
- Takeback support
- Multiple concurrent games
- Automatic stream reconnection
- Works with bullet, blitz, rapid, classical, correspondence

---

## Setup

### 1. Install dependencies
```
pip install -r requirements.txt
```

### 2. Install Stockfish
- Windows: https://stockfishchess.org/download/
- Linux: `sudo apt install stockfish`
- Mac: `brew install stockfish`

### 3. Install Fairy-Stockfish (for variants)
Download from https://github.com/fairy-stockfish/Fairy-Stockfish/releases
Place it in the same folder as Stockfish and update FAIRY_STOCKFISH_PATH in config.py.

### 4. Create a Lichess BOT account
- Make a NEW Lichess account (never played any games)
- Go to https://lichess.org/account/oauth/token/create
- Tick only `bot:play` scope
- Copy the token

### 5. Configure
Create a `.env` file:
```
LICHESS_TOKEN=lip_yourtoken
```
Update `STOCKFISH_PATH` and `FAIRY_STOCKFISH_PATH` in config.py to your engine locations.

### 6. Run
```
python bot.py
```

---

## File structure
```
Lichess_BOT-YourChessPartner/
├── .github/
    ├── ISSUE_TEMPLATE/
        ├── bug_report.md
    ├── workflows/
        ├── bot-ci.yml
        ├── lint-and-test.yml
    ├── pull_request_template.md
├── .vscode/
    ├── settings.json
├── assets/
    ├── books/
        ├── gm2001.bin
├── src/
│   ├── bot.py
│   ├── game_handler.py
│   └── skill_estimator.py
├── tests/
    ├── tests.txt
├── .env.example
├── .gitignore
├── Citation.cff
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── __init__.py
├── pyproject.toml
├── config.py
├── config.yml.default
├── launch_unix.sh
├── launch_windows.bat
├── LICENSE
├── README.md
├── requirements.txt
├── SECURITY.md
├── setup_linux.sh
├── setup_mac.sh
└── setup_windows.ps1
```

---

## Contributing
Pull requests are welcome! If you have ideas for improvements, feel free to open 
an issue or submit a PR. Please credit the original author (Aarav Patel) in any 
forks or distributions.

---

## Known Limitations
- Requires Stockfish and Fairy-Stockfish installed locally
- Needs at least 3 opponent moves before CPL kicks in
- Once upgraded to BOT, the account cannot play as a human anymore
- Needs CMD/PowerShell to be open to play with the bot
  - Windows Tip: Users can launch it silently using pythonw bot.py instead of python bot.py to hide the command prompt window.
  - Linux/Mac Tip: Users can run nohup python bot.py & to safely close their terminal window without killing the bot process.
---

## Credits
- [Stockfish](https://stockfishchess.org/) - Chess engine
- [Fairy-Stockfish](https://github.com/fairy-stockfish/Fairy-Stockfish) - Variant chess engine
- [python-chess](https://python-chess.readthedocs.io/) - Chess library
- [lichess-bot-devs](https://github.com/lichess-bot-devs/lichess-bot) - Bot framework reference (AGPL)

---

## Roadmap
- [ ] Deploy on cloud for 24/7 uptime
- [ ] Web dashboard to monitor live games
- [ ] Custom opening repertoire support
- [ ] ELO tracking over time

---

## FAQ

**Q: Why did the bot decline my draw offer?**
A: The bot only accepts draws when it is losing or the position is equal.

**Q: Why is the bot playing so strong/weak?**
A: The bot adapts to your live centipawn loss, not your rating. If you play accurately it plays stronger.

**Q: Why did the bot resign?**
A: The bot auto-resigns when it detects it is getting mated in 3 or less moves.

**Q: Can I use this bot for training?**
A: Yes! That's exactly what it's designed for.**

---

## Changelog

### v1.0.0 (2026-03-22)
- Initial release
- Live CPL-based adaptive difficulty using UCI_Elo
- Auto-accept challenges
- Smart draw handling
- Auto-resign on forced mate
- Takeback support
- Multiple concurrent games
- Automatic stream reconnection
- Support for 2 chess game types—Classical & Chess960.
---

## Optional: Environment variables
Install python-dotenv for secure token storage:
```
pip install python-dotenv
```
Create a `.env` file:
```
LICHESS_TOKEN=lip_yourtoken
```
Otherwise paste your token directly in config.py.

---

## License
MIT License - Copyright (c) 2026 Aarav Patel
