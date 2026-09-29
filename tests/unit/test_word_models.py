import pytest
from pydantic import ValidationError
from src.extraction.word_models import WordBox, ExtractionMethod

def test_word_box_creation() -> None:
    word_box = WordBox(
        text="Revenue",
        x0=50.0,
        y0=100.0,
        x1=100.0,
        y1=112.0,
        page_number=1,
        extraction_method="native"
    )
    
    assert word_box.width == 50.0
    assert word_box.height == 12.0
    assert word_box.center_x == 75.0
    assert word_box.center_y == 106.0

def test_rejects_reversed_horizontal_coordinates() -> None:
    with pytest.raises(ValidationError):
        WordBox(
            text="Revenue",
            x0=100.0,
            y0=100.0,
            x1=50.0,  # Invalid: x1 should be greater than x0
            y1=112.0,
            page_number=1,
            extraction_method="native"
        )

def test_rejects_reversed_vertical_coordinates() -> None:
    with pytest.raises(ValidationError):
        WordBox(
            text="Revenue",
            x0=50.0,
            y0=112.0,
            x1=100.0,
            y1=100.0,  # Invalid: y1 should be greater than y0
            page_number=1,
            extraction_method="native"
        )

def test_rejects_invalid_confidence() -> None:
    with pytest.raises(ValidationError):
        WordBox(
            text="Revenue",
            x0=50.0,
            y0=100.0,
            x1=100.0,
            y1=112.0,
            page_number=1,
            confidence=1.5,  # Invalid: confidence should be between 0 and 1
            extraction_method="native"
        )