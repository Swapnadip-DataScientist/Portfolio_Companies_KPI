from __future__ import annotations
import argparse
from email.mime import text
import json
from pathlib import Path
from typing import Literal
import fitz
from pydantic import BaseModel, Field

ExtractionRoute = Literal["native_table", "coordinate_reconstruction","native_text", "coordinate_text", "ocr"]

class PageDiagnostic(BaseModel):
    page_number: int = Field(ge=1, description="The page number of the PDF.")
    width: float = Field(gt=0, description="The width of the page in points.")
    height: float = Field(gt=0, description="The height of the page in points.")
    character_count: int = Field(ge=0, description="The number of characters extracted from the page.")
    word_count: int = Field(ge=0, description="The number of words extracted from the page.")
    text_block_count: int = Field(ge=0, description="The number of text blocks extracted from the page.")
    image_count: int = Field(ge=0, description="The number of images extracted from the page.")
    detected_tables_count: int = Field(ge=0, description="The number of tables detected on the page.")
    numeric_token_ratio: float = Field(ge=0, le=1, description="The ratio of numeric tokens to total tokens on the page.")
    has_native_text: bool = Field(description="Indicates if the page has native text.")
    requires_ocr: bool = Field(description="Indicates if the page requires OCR for text extraction.")
    extraction_route: ExtractionRoute = Field(description="The extraction route used for this page.")

class DocumentDiagnostic(BaseModel):
    source_file:str = Field(description="The source file path of the PDF document.")
    file_path: str = Field(description="The path to the PDF document.")
    file_size_bytes: int = Field(ge=0, description="The size of the PDF file in bytes.")
    page_counts: int = Field(ge=1, description="The total number of pages in the document.")
    pages: list[PageDiagnostic] = Field(description="A list of diagnostics for each page in the document.")


def calculate_numeric_token_ratio(words:list[tuple]) -> float:
    """Calculates the ratio of numeric tokens to total tokens in a list of words."""
    if not words:
        return 0.0

    #it means that the word tuple has at least 5 elements, and in the 5th element (index 4) which is assumed to be the text of the word.
    tokens = [str(word[4]).strip() for word in words if len(word) > 4] 
    
    numeric_token = sum(any((character.isdigit() for character in token)) for token in tokens)
       
    return numeric_token / len(tokens)

def select_extraction_route(character_count : int, 
                            word_count : int, detected_tables_count : int, numeric_token_ratio : float) -> ExtractionRoute:

    """Selects the extraction route based on the page content."""
    has_native_text = character_count >= 50 and word_count >= 10

    if detected_tables_count> 0 :
        return "native_table"
    
    if not has_native_text:
        return "ocr"

    has_financial_data = ( word_count >=50 and numeric_token_ratio >= 0.1)

    if has_financial_data:
        return "coordinate_reconstruction"

    return "native_text"


def diagnose_page(page: fitz.Page) -> PageDiagnostic:
    """Diagnoses a single page of a PDF document."""

    text = page.get_text("text")
    words = page.get_text("words")
    detected_table_count = len(page.search_for("Table"))  # Placeholder for actual table detection logic
    blocks = page.get_text("blocks")
    images = page.get_images(full=True)
    table = page.find_tables().tables
    #detected_tables_count = len(page.search_for("Table"))  # Placeholder for actual table detection logic

    character_count = len(text)
    word_count = len(words)
    text_block_count = len(blocks)
    detected_table_count = len(table)
    numeric_token_ratio = round(calculate_numeric_token_ratio(words), 4)
    image_count = len(images)

    route = select_extraction_route(character_count = character_count, word_count = word_count, detected_tables_count = detected_table_count, numeric_token_ratio = numeric_token_ratio)

    return PageDiagnostic(
        page_number=page.number + 1,
        width=page.rect.width,
        height=page.rect.height,
        character_count=character_count,
        word_count=word_count,
        text_block_count=text_block_count,
        image_count=image_count,
        detected_tables_count=detected_table_count,
        numeric_token_ratio=round(numeric_token_ratio, 4),
        has_native_text = route != "ocr",
        requires_ocr = route == "ocr",
        extraction_route=route
    )


def diagnose_document(pdf_path: Path) -> DocumentDiagnostic:
    """Diagnoses a PDF document and returns a DocumentDiagnostic object."""
    pdf_path = Path(pdf_path)

    if not pdf_path.exists() or not pdf_path.is_file():
        raise FileNotFoundError(f"The file {pdf_path} does not exist or is not a file.")

    if not pdf_path.suffix.lower() == ".pdf":
        raise ValueError(f"The file {pdf_path} is not a PDF file.")

    with fitz.open(pdf_path) as doc:

        if doc.page_count == 0:
            raise ValueError(f"The PDF file {pdf_path} has no pages.")

        pages_diagnostics = [diagnose_page(page) for page in doc]

        return DocumentDiagnostic(
            source_file=pdf_path.name,
            file_path=str(pdf_path),
            file_size_bytes=pdf_path.stat().st_size,
            page_counts=len(pages_diagnostics),
            pages=pages_diagnostics
        )


def save_page_diagnostics_to_json(diagnostic : DocumentDiagnostic, output_path: Path) -> None:
                                  
    """Saves the page diagnostics to a JSON file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(diagnostic.model_dump_json(indent=4), encoding="utf-8",)


def parse_arguments() -> argparse.Namespace:
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(description="Diagnose a PDF document and select the extraction routes.")
    parser.add_argument("--input", required = True, type=Path, help="Path to the PDF document.")
    parser.add_argument("--output", required = True, type=Path, help="Path to save the diagnostics JSON file.")
    return parser.parse_args()


def main() -> None:
    """Main function to diagnose a PDF document and save the diagnostics to a JSON file."""
    args = parse_arguments()
    diagnostic = diagnose_document(args.input)
    save_page_diagnostics_to_json(diagnostic, args.output)
    print(f"Diagnostics saved to {args.output}"
          f"\nTotal pages: {diagnostic.page_counts} pages")

    for page in diagnostic.pages:
        print(f"Page {page.page_number}: "
              f"Width: {page.width}, Height: {page.height}, "
              f"Characters: {page.character_count}, Words: {page.word_count}, "
              f"Text Blocks: {page.text_block_count}, Images: {page.image_count}, "
              f"Detected Tables: {page.detected_tables_count}, "
              f"Numeric Token Ratio: {page.numeric_token_ratio:.4f}, "
              f"Has Native Text: {page.has_native_text}, Requires OCR: {page.requires_ocr}, "
              f"Extraction Route: {page.extraction_route}")


if __name__ == "__main__":
    main()


