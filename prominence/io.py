import os
import textgrid

def save_prominence_to_text(results_dict, textgrid_path, wav_path, output_dir="output", tier_name="word"):
    tg = textgrid.TextGrid.fromFile(textgrid_path)
    word_tier = next((t for t in tg.tiers if t.name.lower() == tier_name.lower()), None)
    if word_tier is None:
        raise ValueError(f"No tier named '{tier_name}' found in {textgrid_path}")

    os.makedirs(output_dir, exist_ok=True)

    # Generate output filename from wav file name and tier name
    wav_filename = os.path.splitext(os.path.basename(wav_path))[0]
    filename = f"{wav_filename}_{tier_name}.txt"
    output_path = os.path.join(output_dir, filename)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("word\tstart_time\tend_time\traw_prominence\tnorm_prominence\n")
        for interval in word_tier.intervals:
            word = interval.mark.strip()
            if not word:
                continue
            start = round(interval.minTime, 3)
            end = round(interval.maxTime, 3)
            key = (interval.minTime, word)
            if key in results_dict:
                raw = round(results_dict[key]["raw"], 3)
                norm = round(results_dict[key]["norm"], 3)
                f.write(f"{word}\t{start:.3f}\t{end:.3f}\t{raw:.3f}\t{norm:.3f}\n")

    print(f"Saved prominence file: {output_path}")
