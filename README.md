# 🤖 Lichess-Inappropriate_BOT

![Language](https://shields.io/badge/Language-English-black)
![Engine](https://shields.io/badge/Engine-Stockfish-red)
![License](https://img.shields.io/badge/License-MIT-teal)
![Status](https://img.shields.io/badge/Status-Active-darkgreen)

## 📖 Table of Contents

1. [Introduction](#1-introduction)
2. [Project Goal](#2-project-goal)
3. [Architecture & Workflow](#3-architecture--workflow)
4. [Core Features](#4-core-features)
5. [Prerequisites & System Requirements](#5-prerequisites--system-requirements)
6. [Installation Blueprint](#6-installation-blueprint)
7. [Environment Configuration](#7-environment-configuration)
8. [Comprehensive Directory Mapping](#8-comprehensive-directory-mapping)
9. [Detailed Module Breakdown](#9-detailed-module-breakdown)
10. [Deployed Bot](#10-deployed-bot)
11. [Advanced Usage Framework](#11-advanced-usage-framework)
12. [API & Programmatic Reference](#12-api--programmatic-reference)
13. [Troubleshooting & Diagnostics](#13-troubleshooting--diagnostics)
14. [Performance Fine-Tuning](#14-performance-fine-tuning)
15. [Contributing Lifecycle](#15-contributing-lifecycle)
16. [License Agreements](#16-license-agreements)
17. [Credits and Badges](#17-credits-and-badges)
18. [Future Roadmap](#18-future-roadmap)

---

## 1. Introduction
`Lichess-Inappropriate_BOT` is an open-source, fully automated chess execution engine designed to interface natively with the lichess.org Bot API. Constructed using modern Python workflows, the bot acts as a bridge between asynchronous web streaming loops and local command-line chess engine binaries, processing matches across classical formats and alternative variants flawlessly.

## 2. Project Goal
The ultimate core focus of the project is to build an **Adaptive Chess Partner** that dynamically matches an opponent's real-time playing prowess. By calculating performance on a per-move basis, the framework prevents games from feeling stagnant, creating a flexible environment that tests tactical accuracy dynamically throughout the match lifecycles.

## 3. Architecture & Workflow
The system reads gameplay states continuously via streaming long-lived TCP connections, estimating performance using a specialized rolling calculation matrix:

```
   Game Starts
   │
   ├── [1. Default State]
   │     └── Bot initializes at default ELO 1200
   │
   ├── [2. Live Tracking Loop]
   │     ├── Monitors opponent moves continuously
   │     └── Calculates rolling average Centipawn Loss (CPL)
   │
   ├── [3. Dynamic Mapping Phase]
   │     ├── CPL ≤ 15   ➔ ELO 2200 (Master)
   │     ├── CPL ≤ 25   ➔ ELO 2000 (Expert)
   │     ├── CPL ≤ 40   ➔ ELO 1800 (Strong Club)
   │     ├── CPL ≤ 60   ➔ ELO 1600 (Intermediate)
   │     ├── CPL ≤ 90   ➔ ELO 1400 (Casual)
   │     ├── CPL ≤ 130  ➔ ELO 1200 (Beginner)
   │     └── CPL > 130  ➔ ELO 1000 (Newcomer)
   │
   └── [4. Lock-In Phase]
         └── Enforces calculated target ELO for remaining game matrix
```

## 4. Core Features
* **Live CPL Scaling:** Real-time optimization updates that dynamically scale difficulty setting attributes.
* **Variant Integration:** Full execution compatibility with all variants supported by Fairy-Stockfish.
* **Smart Draw Strategy:** Rejects draw queries when holding advantages; accepts when under heavy strain.
* **Predictive Resignations:** Instantly detects unpreventable forced checkmates in 3 moves or fewer.
* **Concurrent Scaling:** Handles multiple asynchronous platform matches running at once.

## 5. Prerequisites & System Requirements
* **Runtime Core:** Python 3.10 or newer (configured along with local virtual environments).
* **Engines:** Local system execution paths pointing to standard Stockfish or Fairy-Stockfish binaries.
* **Platform Constraints:** A dedicated, unplayed Lichess profile upgraded strictly to a `BOT` status.

## 6. Installation Blueprint
To deploy using the pre-compiled Python distribution packaging wheels, run the installation sequence directly through your tool terminal:
```bash
pip install inappropriate_bot-1.0.0-py3-none-any.whl
```
To run directly from the raw source code compression archive, unpack the package components manually:
```bash
tar -xvf inappropriate_bot-1.0.0.tar.gz
cd inappropriate_bot-1.0.0
pip install -r requirements.txt
```

## 7. Environment Configuration
The application consumes standard credentials through an active `.env` configuration template or a localized configuration layout. Create a `config.yml` block in your workspace path:
```yaml
token: "lip_YOUR_SECURE_LICHESS_API_TOKEN"
engine:
  path: "./stockfish-windows-x86-64-avx2.exe"
  variants: "./fairy-stockfish-largeboard_x86-64.exe"
```
Alternatively, apply configuration rules directly using a root `.env` template parameter configuration:
```env
LICHESS_TOKEN=lip_yourtoken
```

## 8. Comprehensive Directory Mapping
```text
Lichess-Inappropriate_BOT/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   └── bug_report.md
│   └── workflows/
│       ├── bot-ci.yml
│       ├── lint-and-test.yml
│       └── publish.yml
│   ├── pull_request_template.md
├── .vscode/
│   └── settings.json
├── config/
│   ├── bot_config.py
│   └── config.yml.default
├── src/
│   ├── RateLimit429Stopper.py
│   ├── __init__.py
│   ├── bot.py
│   ├── game_handler.py
│   └── skill_estimator.py
└── tests/
    └── config.xml.default
├── .env.example
├── .gitattributes
├── .gitignore
├── CITATION.cff
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── Dockerfile
├── LICENSE
├── README.md
├── SECURITY.md
├── app.py
├── build.sh
├── cron-job.py
├── error.py
├── launch_unix.sh
├── launch_windows.bat
├── pyproject.toml
├── requirements.txt
├── setup_linux.sh
├── setup_mac.sh
├── setup_windows.ps1
```

## 9. Detailed Module Breakdown
* **`src/bot.py`**: Boots the foundational framework runtime, sets up thread pools, and listens to event pipes.
* **`src/game_handler.py`**: Implements state rules, reads board steps, and processes challenge transactions.
* **`src/skill_estimator.py`**: Tracks analytical evaluation metrics to map centipawn metrics directly onto target ratings.

## 10. Deployed Bot
The backend server is live on Render: [Live Server Status](https://lichess-inappropriate-bot.onrender.com/)

**How to Play / Interact**
Since this is a backend Lichess bot, you don't interact with the Render link directly. Instead:
1. Go to **Lichess.org**.
2. Search for the bot's username: `Inappropriate-BOT`.
3. Challenge the bot to a game or send it a message to see it in action!


## 11. Advanced Usage Framework
Launch the tool package command interface execution entry point natively via the active console window:
```bash
inappropriate_bot
```
For deep application tracing or to enforce active execution visibility without immediate background detachment, run the raw script modules via:
```bash
python -m src.bot
```
* **Silent Mode Execution (Windows):** Suppress the command console pop-up layer by utilizing `pythonw bot.py`.
* **Detached Runtime (Linux/Mac):** Maintain long-term execution after dropping SSH sessions via `nohup python bot.py &`.

## 12. API & Programmatic Reference
The internal handlers parse data properties streaming from Lichess's public development entry channels:
* `GET /api/stream/event`: Establishes the real-time event pipeline to intercept Incoming game challenges.
* `POST /api/bot/game/{gameId}/move/{move}`: Ships calculated chess engine calculations back to the board matrix.
* `POST /api/bot/game/{gameId}/chat`: Emits automated status alerts directly to the in-game log panel.

## 13. Troubleshooting & Diagnostics
* **Flashing Window/Instant Exit:** Avoid clicking raw module paths directly from the explorer window. Launch the module commands manually from an already open terminal window to capture active error flags.
* **401 Authentication Validation Errors:** Confirm your token features the authorized `bot:play` permission configuration.
* **Engine Connection Timeout:** Ensure path variables in `config.py` point directly to legitimate engine instances.

## 14. Performance Fine-Tuning
Optimize your engine properties for low-latency calculations:
* **Core Distribution:** Align the calculation process properties explicitly with actual machine CPU core limitations.
* **Hash Optimization:** Raise local allocation ceilings (e.g., to 2048MB) within your script configuration values to accelerate high-depth searches.

## 15. Contributing Lifecycle
We welcome pull requests and enhancements. Review the comprehensive style standards, pipeline conditions, and branch submission structures maintained in our [`CONTRIBUTING.md`](./CONTRIBUTING.md) configuration layout.

## 16. License Agreements
This codebase is entirely open-source software distributed under the terms of the **MIT License**. For complete copyright parameters, review the root [`LICENSE`](./LICENSE) text asset. This framework acts as a bridge reference derived from the original engine systems managed under the AGPL open-source guidelines.

## 17. Credits and Badges
* Developed utilizing foundational structural wrappers provided by the [lichess-bot-devs](https://github.com/lichess-bot-devs/lichess-bot) community team.
* Core engine operations run via official [Stockfish](https://stockfishchess.org/) and [Fairy-Stockfish](https://github.com/fairy-stockfish/Fairy-Stockfish) projects.
* Object representations managed inside Python using the open-source [python-chess](https://python-chess.readthedocs.io/) runtime package library.

## 18. Future Roadmap
* [] Integrate native web dashboard interfaces to keep track of active match histories.
* [✓] Support customized cloud hosting integration setups for true 24/7 uptime.
* [] Automate opening database selections according to opponent account configurations.
* [] Support all Lichess Variants.
