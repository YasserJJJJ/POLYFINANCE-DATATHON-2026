import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
# Les tests sont déterministes : aucun appel à Bedrock.
os.environ.setdefault("ALPHAFORGE_LLM", "off")
