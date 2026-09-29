from collections import defaultdict

from src.extraction.word_models import WordBox


def group_words_into_rows(
    words: list[WordBox],
    y_tolerance: float = 3.0,
) -> list[list[WordBox]]:
    """Group words on the same page with similar vertical centres."""

    words_by_page: dict[int, list[WordBox]] = defaultdict(list)

    for word in words:
        words_by_page[word.page_number].append(word)

    reconstructed_rows: list[list[WordBox]] = []

    for page_number in sorted(words_by_page):
        page_words = sorted(
            words_by_page[page_number],
            key=lambda word: (word.center_y, word.x0),
        )

        current_row: list[WordBox] = []
        current_center_y: float | None = None

        for word in page_words:
            if current_center_y is None:
                current_row = [word]
                current_center_y = word.center_y
                continue

            if abs(word.center_y - current_center_y) <= y_tolerance:
                current_row.append(word)
                current_center_y = sum(item.center_y for item in current_row) / len(current_row)
            else:
                reconstructed_rows.append(sorted(current_row, key=lambda item: item.x0))
                current_row = [word]
                current_center_y = word.center_y

        if current_row:
            reconstructed_rows.append(sorted(current_row, key=lambda item: item.x0))

    return reconstructed_rows


def reconstruct_row_text(row: list[WordBox]) -> str:
    """Join horizontally ordered words into readable row text."""

    return " ".join(word.text for word in row)