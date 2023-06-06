import subprocess
import os


with open('output.log', 'w') as output_file:
        process = subprocess.Popen(['python3', 'game/FlappyBird.py'], stdout=output_file, stderr=subprocess.STDOUT)
