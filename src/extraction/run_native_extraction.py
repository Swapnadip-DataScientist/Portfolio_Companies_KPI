from pathlib import Path
import argparse
from collections import Counter

from src.extraction.native_word_extractor import extract_native_words

def main()-> None : 

    parser = argparse.ArgumentParser()
    parser.add_argument("--input" , type=Path, required=True)
    args = parser.parse_args()


    words = extract_native_words(args.input)
    page_counts = Counter(word.page_number for word in words)

    print(f"\nFile: {args.input.name}")
    print(f"Total words: {len(words)}")

    for page_number, count in sorted(page_counts.items()):
        print(f"Page {page_number}: {count} words")

    print("\nFirst 10 WordBox objects:")

    for word in words[:10]:

        print(
                f"Page={word.page_number}, Text ={word.text!r} "
                f"Box=({word.x0}, {word.y0}, {word.x1}, {word.y1}), "
                f"Center=({word.center_x:.2f}, {word.center_y:.2f})"
        )

if __name__ == "__main__":
    main()
        




