import argparse
import os
import sys

# Ensure project root is consistent (folder where this script lives)
script_dir = os.path.dirname(os.path.realpath(__file__))
project_root = os.path.abspath(os.path.join(script_dir))
sys.path.append(project_root)

from prominence.extract import extract_word_prominence_from_prosody
from prominence.io import save_prominence_to_text

def main():
    parser = argparse.ArgumentParser(description="Batch extract prosodic prominence from audio/TextGrid files.")
    parser.add_argument("--data_dir", type=str, required=True, help="Directory containing .wav and .TextGrid files")
    parser.add_argument("--tier", type=str, default="word", help="Tier name to extract from")
    parser.add_argument("--utt_threshold", type=float, default=0.3, help="Silence threshold for utterance split")
    parser.add_argument("--lambda_", type=float, default=0.5, help="Weight for mid-band energy")
    parser.add_argument("--beta_", type=float, default=0.5, help="Weight for prosodic dynamics")

    # Save to 'output' folder inside ProsodicProminenceExtractor project
    default_output = os.path.join(project_root, "output")
    parser.add_argument("--output_dir", type=str, default=default_output, help="Directory to save output .txt files")

    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    file_pairs_found = 0

    for root, _, files in os.walk(args.data_dir):
        print(f"Searching in: {root}")
        for file in files:
            if file.endswith(".TextGrid"):
                base = os.path.splitext(file)[0]
                tg_path = os.path.join(root, file)

                wav_path = os.path.join(root, base + ".wav")
                raw_path = os.path.join(root, base)

                # Check for either .wav or extensionless file
                if os.path.exists(wav_path):
                    audio_path = wav_path
                elif os.path.exists(raw_path):
                    audio_path = raw_path
                else:
                    print(f" Skipping {base}: No matching audio file found (.wav or extensionless).")
                    continue

                print(f"Found pair: {audio_path} + {tg_path}")
                try:
                    results = extract_word_prominence_from_prosody(
                        audio_path, tg_path,
                        tier_name=args.tier,
                        utt_threshold=args.utt_threshold,
                        lambda_=args.lambda_,
                        beta_=args.beta_
                    )

                    save_prominence_to_text(
                        results,
                        textgrid_path=tg_path,
                        wav_path=audio_path,
                        output_dir=args.output_dir,
                        tier_name=args.tier
                    )

                    file_pairs_found += 1
                except Exception as e:
                    print(f"Error processing {base}: {e}")

    print("\n===================================")
    if file_pairs_found > 0:
        print(f"Processed {file_pairs_found} file(s). Results saved to:\n   {args.output_dir}")
    else:
        print("No valid .wav + .TextGrid pairs found or No valid tier named found. Nothing was processed.")
    print("===================================\n")

if __name__ == "__main__":
    main()
