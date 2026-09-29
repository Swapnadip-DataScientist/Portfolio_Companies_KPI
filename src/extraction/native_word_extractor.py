from pathlib import Path
import pymupdf
from src.extraction.word_models import WordBox

def tuple_to_word_box(raw_word: tuple, page_number: int) -> WordBox:
    """Converts a word tuple from PyMuPDF to a WordBox object."""
    x0, y0, x1, y1, text, block_no, line_no, word_no  = raw_word 

    return WordBox(
        text=str(text).strip(),
        x0=round(float(x0),3),
        y0=round(float(y0),3),
        x1=round(float(x1),3),
        y1=round(float(y1),3),
        page_number=page_number,
        block_number = int(block_no),
        line_number = int(line_no),
        word_number = int(word_no),
        confidence = None,
        extraction_method="native"
    )

def extract_native_words(pdf_path : Path ) -> list[WordBox]:

    if not pdf_path.exists():
        raise FileNotFoundError(f"Expected a PDF file: {pdf_path}")

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Expected a PDF file: {pdf_path}")

    extracted_words :list[WordBox] =[]

    with pymupdf.open(pdf_path) as document:

        for page in document:

            raw_words = page.get_text("words", sort= True)

            for raw_word in raw_words:

                if not str(raw_word[4]).strip():
                    continue

                extracted_words.append(tuple_to_word_box
                                       (raw_word=raw_word, 
                                        page_number=page.number +1
                                        )
                                    )
    return extracted_words