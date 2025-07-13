# ProsodicProminenceExtractor

**ProsodicProminenceExtractor** is an open-source Python tool that extracts **word-level or phone-level prosodic prominence** from speech recordings using `.wav` audio and aligned `.TextGrid` annotations. It calculates prominence using pitch, energy, and event dynamics, with support for utterance-level normalization.

---

## What the Tool Does

- Computes **prosodic prominence scores** for each annotated word or phone interval.
- Uses a combination of:
  - RMS energy
  - Mid-band energy (300–2200 Hz)
  - Pitch-based rise/fall dynamics (event-based)
- Supports **custom tier selection** from TextGrid (e.g., `"words"`, `"phones"`).
- Allows **custom weighting** of acoustic and dynamic features via `lambda` and `beta`.
- Supports **utterance-based normalization**.
- Works via **CLI**, **demo script**, or as an importable Python module.

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/arunps12/ProsodicProminenceExtractor.git
cd ProsodicProminenceExtractor
```

### 2. Create and activate a virtual environment
```bash
python -m venv prosody_env
```
# On Windows
```bash
prosody_env\Scripts\activate
```
# On macOS/Linux
```bash
source prosody_env/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. After setup, run the command-line interface:
```bash
python cli.py --data_dir data/ --tier "your_tier_name" --lambda_ 0.5 --beta_ 0.5
```
-- This will automatically process all .wav and .TextGrid file pairs in the data/ directory that share the same base filename (e.g., example.wav and example.TextGrid).

# Arguments:

- data_dir: Path to the folder containing .wav and .TextGrid files

- tier: Name of the tier to extract prominence from (e.g., "word", "phones")

- utt_threshold:    Minimum silence duration (in seconds) to split utterances (default: 0.3)

- lambda_:  Weight for mid-band energy (default = 0.5)

- beta_:    Weight for dynamic prosody (pitch-energy interaction) (default = 0.5)

- output_dir:   Path to save output .txt files (default: output/)

# Example Output
```bash
word	start_time	end_time	raw_prominence	norm_prominence
hello	0.51	       0.72	        2.439	        0.873
```
# To run a quick demo with default paths, use:
```bash
python examples/demo_extract.py
```
# Your TextGrid tier should contain labeled intervals for words or phones like this:
```bash
IntervalTier "words" ...
"hello" 0.50–0.72
"how"  0.74–1.02
```
# License
This project is licensed under the MIT License. See the LICENSE file for more information.

# Contributing
Feel free to open issues or submit pull requests to improve this tool. Feature suggestions, bug reports, and enhancements are welcome.

# Repository Structure
```bash
ProsodicProminenceExtractor/
├── prominence/
│   ├── extract.py         # Core extraction logic
│   ├── io.py              # File saving utilities
│
├── examples/
│   └── demo_extract.py    # Simple demo script
│
├── cli.py                 # Command-line interface
├── requirements.txt       # Python dependencies
├── README.md              # Documentation
├── .gitignore             # Ignored files
```