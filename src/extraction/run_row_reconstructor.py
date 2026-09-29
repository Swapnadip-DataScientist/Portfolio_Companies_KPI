import argparse
from pathlib import Path

from src.extraction.native_word_extractor import extract_native_words
from src.extraction.row_constructor import (
    group_words_into_rows,
    reconstruct_row_text,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()

    words = extract_native_words(args.input)
    rows = group_words_into_rows(words)

    print(f"\nFile: {args.input.name}")
    print(f"Total words: {len(words)}")
    print(f"Reconstructed rows: {len(rows)}")
    print("\nRemaining 25 reconstructed rows:")

    for row_number, row in enumerate(rows[24:], start=25):
        row_text = reconstruct_row_text(row)
        print(
            f"Row {row_number:02d} | "
            f"Page {row[0].page_number} | "
            f"Y={row[0].center_y:.2f} | "
            f"{row_text}"
        )


if __name__ == "__main__":
    main()