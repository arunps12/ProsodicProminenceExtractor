import argparse
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from prominence.extract import extract_word_prominence_from_prosody
from prominence.io import save_prominence_to_text

def main():
    parser = argparse.ArgumentParser(description="Batch extract prosodic prominence from audio/TextGrid files.")
    parser.add_argument("--data_dir", type=str, required=True, help="Directory containing .wav and .TextGrid files")
    parser.add_argument("--tier", type=str, default="word", help="Tier name to extract from")
    parser.add_argument("--utt_threshold", type=float, default=0.2, help="Silence threshold for utterance split")
    parser.add_argument("--lambda_", type=float, default=0.5, help="Weight for mid-band energy")
    parser.add_argument("--beta_", type=float, default=0.5, help="Weight for prosodic dynamics")

    # Always save in output folder inside project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    default_output = os.path.join(project_root, "output")
    parser.add_argument("--output_dir", type=str, default=default_output, help="Directory to save output .txt files")

    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # Recursively find .wav files and corresponding TextGrids
    for root, _, files in os.walk(args.data_dir):
        for file in files:
            if file.endswith(".wav"):
                base = os.path.splitext(file)[0]
                wav_path = os.path.join(root, file)
                tg_path = os.path.join(root, base + ".TextGrid")

                if not os.path.exists(tg_path):
                    print(f" Skipping {base} — TextGrid not found")
                    continue

                print(f" Processing: {base}")
                try:
                    results = extract_word_prominence_from_prosody(
                        wav_path, tg_path,
                        tier_name=args.tier,
                        utt_threshold=args.utt_threshold,
                        lambda_=args.lambda_,
                        beta_=args.beta_
                    )

                    save_prominence_to_text(
                        results,
                        textgrid_path=tg_path,
                        wav_path=wav_path,
                        output_dir=args.output_dir,
                        tier_name=args.tier
                    )
                except Exception as e:
                    print(f"Error processing {base}: {e}")

    print(f"\n Batch processing complete. Results saved to: {args.output_dir}")

if __name__ == "__main__":
    main()
