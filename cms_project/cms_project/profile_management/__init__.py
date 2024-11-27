import sys
from pathlib import Path

# Add models and views directories to the Python path
sys.path.append(str(Path(__file__).resolve().parent / "models"))
sys.path.append(str(Path(__file__).resolve().parent / "views"))
