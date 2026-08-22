# 🤖 Lichess-MakeChessBetter

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
`Lichess-MakeChessBetter` is an open-source, fully automated chess execution engine designed to interface natively with the lichess.org Bot API. Constructed using modern Python workflows, the bot acts as a bridge between asynchronous web streaming loops and local command-line chess engine binaries, processing matches across classical formats and alternative variants flawlessly.

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
pip install MakeChessBetter-1.0.0-py3-none-any.whl
```
To run directly from the raw source code compression archive, unpack the package components manually:
```bash
tar -xvf MakeChessBetter-2.0.1.tar.gz
cd MakeChessBetter-2.0.1
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

## 8. Comprehensive Directory Mapping and Explanation
```text
Lichess-MakeChessBetter/
├── .github/                                  # GitHub configuration and automation files
│   ├── ISSUE_TEMPLATE/                       # Templates for creating new repository issues
│   │   └── bug_report.md                     # Standard form for reporting software bugs
│   └── workflows/                            # Automated CI/CD pipeline script files
│       ├── bot-ci.yml                        # Automates continuous integration for the bot
│       ├── lint-and-test.yml                 # Automatically checks code quality and tests
│       └── publish.yml                       # Automates publishing releases of the bot
│   └── pull_request_template.md              # Template for submitting new code changes
├── .vscode/                                  # Visual Studio Code editor settings
│   └── settings.json                         # Custom workspace configurations for Visual Studio
├── config/                                   # Project configuration files and blueprints
│   ├── bot_config.py                         # Python script handling bot configuration logic
│   └── config.yml.default                    # Default template for main application settings
├── docs/                                     # Project documentation files
│   └── source/                               # Source documentation files
│       └── conf.py                           # Configuration file for Sphinx documentation generator
├── src/                                      # Primary executable Python source code
│   ├── RateLimit429Stopper.py                # Prevents exceeding Lichess API rate limits
│   ├── __init__.py                           # Marks directory as a Python package
│   ├── bot.py                                # Main script running the chess bot
│   ├── game_handler.py                       # Manages live chess gameplay and moves
│   ├── history_manager.py                    # Records and tracks past game logs
│   ├── openings.py                           # Handles chess opening book move selections
│   ├── scout.py                              # Analyzes opponents before starting a game
│   ├── skill_estimator.py                    # Evaluates and predicts opponent playing strength
├── tests/                                    # Automated scripts checking code correctness
│   └── config.xml.default                    # Default template for XML layout configurations
├── .env.example                              # Example template for environment variable keys
├── .gitattributes                            # Defines attributes for Git repository matching
├── .gitignore                                # Specifies files Git should always ignore
├── .readthedocs.yaml                         # Configuration file for Read the Docs hosting
├── CITATION.cff                              # Provides instructions for citing this repository
├── CODE_OF_CONDUCT.md                        # Rules for community behavior and engagement
├── CONTRIBUTING.md                           # Guidelines for submitting open source contributions
├── Dockerfile                                # Automation blueprint for building container images
├── LICENSE                                   # Legal license terms for using code
├── README.md                                 # Main overview and documentation for project
├── SECURITY.md                               # Instructions for reporting discovered security vulnerabilities
├── app.py                                    # Entry point for launching the application
├── build.sh                                  # Shell script automating project compilation steps
├── cron-job.py                               # Script running scheduled background automation tasks
├── dashboard.py                              # Web dashboard interface for bot statistics
├── error.py                                  # Centralized handling and logging of errors
├── launch_unix.sh                            # Bash script launching bot on Linux
├── launch_windows.bat                        # Batch file launching bot on Windows
├── pyproject.toml                            # Modern packaging and dependency configuration file
├── requirements.txt                          # List of required Python external libraries
├── setup_linux.sh                            # Installation script for Linux operating systems
├── setup_mac.sh                              # Installation script for macOS operating systems
├── setup_windows.ps1                         # PowerShell script setting up Windows environments
└── test_pipeline.py                          # Runs full sequence of automated tests
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
MakeChessBetter
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
* [x] Integrate native web dashboard interfaces to keep track of active match histories.
* [x] Support customized cloud hosting integration setups for true 24/7 uptime.
* [x] Automate opening database selections according to opponent account configurations.
* [ ] Support all Lichess Variants.
