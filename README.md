# ProsodicProminenceExtractor

**ProsodicProminenceExtractor** is an open-source Python tool that extracts **word-level prosodic prominence** from speech recordings using `.wav` audio and aligned `.TextGrid` annotations. It calculates prominence using pitch, energy, and event-based dynamics, with support for utterance-level normalization.

You can control the prominence calculation by adjusting two key parameters:

- **`lambda_`**: Weight for mid-band energy (default = `0.5`)  
  Controls the importance of amplitude-based cues from the mid-frequency band (300–2200 Hz). Increase this to emphasize energy-related prominence.

- **`beta_`**: Weight for dynamic prosody (pitch-energy interaction) (default = `0.5`)  
  Emphasizes event-based changes in pitch and energy. Increase this to focus more on pitch movement or expressive intonation.

These values can be customized depending on your dataset and analysis goals. For example:

- Emphasize energy-based prominence:
  ```bash
  --lambda_ 0.7 --beta_ 0.3¨
  ```
- Emphasize pitch dynamics:
 ```bash
--lambda_ 0.2 --beta_ 0.7
  ```
- Balanced influence:
 ```bash
--lambda_ 0.5 --beta_ 0.5
  ```

---

## What the Tool Does

- Computes **prosodic prominence scores** for each annotated word interval.
- Uses a combination of:
  - RMS energy
  - Mid-band energy (300–2200 Hz)
  - Pitch-based rise/fall dynamics (event-based)
- Supports **custom tier selection** from TextGrid (e.g., `"words"`).
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
python prom.py --data_dir /path/to/your/data --tier "your_tier_name" --lambda_ 0.5 --beta_ 0.5 --output_dir /path/to/your/output
```
- data_dir should be the main folder where your audio (.wav) and TextGrid (.TextGrid) files are stored.

- You can paste multiple .wav and .TextGrid files directly into this folder if they all use the same tier name (e.g., "word"). In this case, just provide that tier name once using --tier.

- If your files have different tier names, you should create subfolders, where each folder contains files with the same tier name. The script will go through each subfolder and apply the tier name you provide.

- .wav and .TextGrid files share the same base filename (e.g., example.wav and example.TextGrid)

- The script will automatically:
  -  Go through the base folder and all its subfolders.
  -  Match each .wav file with a .TextGrid file that has the same filename.
  -  Extract prominence using the tier you specify with --tier.

- The script saves results automatically in the --output_dir folder.
  -  Output filenames are based on the input file and tier name (e.g., S105_word.csv).

- You can also place your .wav and .TextGrid files or folders directly inside the default project data/ folder and pass that as --data_dir.

# Arguments:

- data_dir: Path to the folder containing .wav and .TextGrid files 

- tier: Name of the tier to extract prominence from (e.g., "words")

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
# Your TextGrid tier should contain labeled intervals for words like this:
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
├── prom.py                 # Command-line interface
├── requirements.txt       # Python dependencies
├── README.md              # Documentation
├── .gitignore             # Ignored files
```