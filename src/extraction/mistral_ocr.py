import base64
import os
from pathlib import Path

from dotenv import load_dotenv
from mistralai.client import Mistral


def extract_pdf(pdf_path: Path):
    pdf_path = Path(pdf_path)
    if not pdf_path.is_file():
        raise FileNotFoundError(pdf_path)

    project_root = Path(__file__).resolve().parents[2]
    load_dotenv(project_root / ".env")
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY is missing from .env")

    encoded_pdf = base64.b64encode(pdf_path.read_bytes()).decode("ascii")
    client = Mistral(api_key=api_key)
    return client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": f"data:application/pdf;base64,{encoded_pdf}",
        },
        table_format="html",
    )

def save_ocr_result(result, pdf_path: Path, output_path: Path) -> None:
    import json

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "source_pdf": str(Path(pdf_path).resolve()),
        "ocr_result": result.model_dump(mode="json"),
    }
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )