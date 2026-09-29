import argparse
from pathlib import Path

from src.extraction.mistral_ocr import extract_pdf, save_ocr_result


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract PDFs with Mistral OCR")
    parser.add_argument("pdfs", nargs="+", type=Path, help="PDF files to process")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[2]

    for pdf in args.pdfs:
        result = extract_pdf(pdf)
        output = (
            project_root
            / "data"
            / "extracted"
            / pdf.parent.name
            / f"{pdf.stem}_ocr.json"
        )
        save_ocr_result(result, pdf, output)
        print(f"Saved {len(result.pages)} pages to {output}")


if __name__ == "__main__":
    main()