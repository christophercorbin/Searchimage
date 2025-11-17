# Configure pytest to add the root of the project to the PYTHONPATH
import sys
import os

# Add the root of your project to PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
