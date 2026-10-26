"""
Small helper that tells the rest of the project where it lives.

The original course code used a hard coded path such as
"/Users/Vmaha/Desktop/Bitcoin", which only works on the author's machine.
Everything here is worked out from the location of this file instead, so the
project runs from any folder on any drive.
"""

from pathlib import Path

# .../Humayl_Zafer_24k-5604_Blockchain
PROJECT_ROOT = Path(__file__).resolve().parents[3]

# Folder where the blockchain and the wallet keys are stored.
DATA_DIR = PROJECT_ROOT / "data"

# Port used by the small Flask wallet page.
WEB_PORT = 5900
