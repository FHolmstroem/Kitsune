import os
import sys
from pathlib import Path

this_file = Path(__file__).resolve()

# 1. ALWAYS load the 'src' folder from the current working directory FIRST.
# If mutmut is running, this forces tests to use the mutated files in the sandbox.
sandbox_src = Path(os.getcwd()) / "src"
sys.path.insert(0, str(sandbox_src))

# 2. If we are trapped in the sandbox, load the REAL src folder as a BACKUP.
# This allows tests to find animation.py and other files mutmut didn't copy.
if "mutants" in this_file.parts:
    real_root = this_file.parent.parent.parent
    sys.path.insert(1, str(real_root / "src"))

# 3. Keep Qt headless
os.environ["QT_QPA_PLATFORM"] = "offscreen"