import os
import sys

# Add project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from prominence.extract import extract_word_prominence_from_prosody
from prominence.io import save_prominence_to_text

# Paths (relative to project root)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Build paths to the data folder
wav_path = os.path.join(project_root, "data", "example.wav")
tg_path = os.path.join(project_root, "data", "example.TextGrid")
output_dir = os.path.join(project_root, "output")

# extraction and save results
results = extract_word_prominence_from_prosody(wav_path, tg_path, tier_name="UIT001 - words", lambda_=0.5, beta_=0.5)
save_prominence_to_text(results, tg_path, wav_path, output_dir=output_dir, tier_name="UIT001 - words")
