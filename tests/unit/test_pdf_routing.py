import pytest
from src.diagnostics.pdf_diagnostics import select_extraction_route, ExtractionRoute

#Instead of writing six separate test functions, we pass six input scenarios through the same test.
@pytest.mark.parametrize(
    "character_count, word_count, detected_tables_count, numeric_token_ratio, expected_route",
    [
        (0, 0, 0, 0.00, "ocr"),
        (40, 8, 0, 0.25, "ocr"),
        (500, 100, 1, 0.20, "native_table"),
        (1000, 175, 0, 0.2286, "coordinate_reconstruction"),
        (1000, 177, 0, 0.1356, "coordinate_reconstruction"),
        (1000, 200, 0, 0.05, "native_text"),
    ]
)
def test_select_extraction_route(
    character_count: int,
    word_count: int,
    detected_tables_count: int,
    numeric_token_ratio: float,
    expected_route: ExtractionRoute
):
    route = select_extraction_route(
        character_count=character_count,
        word_count=word_count,
        detected_tables_count=detected_tables_count,
        numeric_token_ratio=numeric_token_ratio
    )
    assert route == expected_route