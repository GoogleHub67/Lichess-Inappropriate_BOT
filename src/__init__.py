import sys
import os

# Force Python to look inside the src folder directly
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Now Python can safely find the files inside src/
import bot
import game_handler
import skill_estimator
