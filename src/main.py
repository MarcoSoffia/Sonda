import Chunker
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
file_path = BASE_DIR / "requirements.txt"

# Read, Bytes
with open(file_path, "rb") as f:
    file = f.read()

chunker = Chunker.Chunker(file)

chunks = chunker.chunk()

[print(chunk) for chunk in chunks]

