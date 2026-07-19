import sys
import os
# This forces python to see your src files
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

import bot
import skill_estimator
import game_handler

print("Everything is fully resolved!")
