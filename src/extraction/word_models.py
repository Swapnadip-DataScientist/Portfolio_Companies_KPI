from typing import Literal
from pydantic import BaseModel, Field, model_validator


ExtractionMethod = Literal["native", "ocr"]

class WordBox(BaseModel):
    text: str = Field(min_length=1) #Empty text is rejected.
    x0: float = Field(ge=0)
    y0: float = Field(ge=0)
    x1: float = Field(gt=0)
    y1: float = Field(gt=0)
    page_number: int = Field(ge=1)
    block_number: int | None = Field(default=None, ge=0)
    line_number: int | None = Field(default=None, ge=0)
    word_number: int | None = Field(default=None, ge=0)
    confidence: float | None = Field(default=None, ge=0, le=1)
    extraction_method: ExtractionMethod

    @model_validator(mode="after")
    def validate_bounding_box(self) -> "WordBox":
        if self.x1 <= self.x0:
            raise ValueError("x1 must be greater than x0")

        if self.y1 <= self.y0:
            raise ValueError("y1 must be greater than y0")

        return self

    @property
    def width(self) -> float:
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        return self.y1 - self.y0

    @property
    def center_x(self) -> float:
        return (self.x0 + self.x1) / 2

    @property
    def center_y(self) -> float:
        return (self.y0 + self.y1) / 2