import argparse
import os
import sys
# Add project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from prominence.extract import extract_word_prominence_from_prosody
from prominence.io import save_prominence_to_text

def main():
    parser = argparse.ArgumentParser(description="Extract prosodic prominence from audio and TextGrid files.")
    parser.add_argument("wav_path", type=str, help="Path to the input .wav file")
    parser.add_argument("textgrid_path", type=str, help="Path to the corresponding TextGrid file")
    parser.add_argument("--tier", type=str, default="word", help="Name of the tier (e.g., word, phones)")
    parser.add_argument("--utt_threshold", type=float, default=0.2, help="Minimum silence to split utterances (seconds)")
    parser.add_argument("--lambda_", type=float, default=0.5, help="Weight for mid-band energy")
    parser.add_argument("--beta_", type=float, default=0.5, help="Weight for dynamic prosodic contribution")
    parser.add_argument("--output_dir", type=str, default="output", help="Directory to save results")

    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    results = extract_word_prominence_from_prosody(
        args.wav_path,
        args.textgrid_path,
        tier_name=args.tier,
        utt_threshold=args.utt_threshold,
        lambda_=args.lambda_,
        beta_=args.beta_
    )

    save_prominence_to_text(
        results,
        textgrid_path=args.textgrid_path,
        wav_path=args.wav_path,
        output_dir=args.output_dir,
        tier_name=args.tier
    )

    print(f"Prominence extraction completed. Results saved to {args.output_dir}")

if __name__ == "__main__":
    main()
