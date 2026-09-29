import base64
from unittest.mock import Mock
import json
import sys

from src.extraction import run_mistral_ocr

from src.extraction import mistral_ocr


def test_extract_pdf_sends_entire_pdf(monkeypatch, tmp_path):
    pdf = tmp_path / "sample.pdf"
    pdf.write_bytes(b"%PDF-1.4\nsynthetic test content")

    monkeypatch.setenv("MISTRAL_API_KEY", "test-key")
    fake_client = Mock()
    fake_client.ocr.process.return_value = "mock OCR result"
    monkeypatch.setattr(mistral_ocr, "Mistral", Mock(return_value=fake_client))

    result = mistral_ocr.extract_pdf(pdf)

    assert result == "mock OCR result"
    request = fake_client.ocr.process.call_args.kwargs
    assert request["model"] == "mistral-ocr-latest"
    assert request["table_format"] == "html"
    assert "pages" not in request
    encoded = request["document"]["document_url"].split(",", 1)[1]
    assert base64.b64decode(encoded) == pdf.read_bytes()

def test_save_ocr_result_preserves_page_data(tmp_path):

    pdf = tmp_path/"sample.pdf"
    output = tmp_path/ "extracted" / "sample_ocr.json"

    response = Mock()
    response.model_dump.return_value ={ "pages": [{"index": 0, "markdown": "Revenue: 100", "tables": []}]}

    mistral_ocr.save_ocr_result(response, pdf, output)

    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved["source_pdf"] == str(pdf.resolve())
    assert saved["ocr_result"]["pages"][0]["index"] == 0
    assert saved["ocr_result"]["pages"][0]["markdown"] == "Revenue: 100"




def test_runner_creates_separate_outputs(monkeypatch, tmp_path):
    first = tmp_path / "Company_ABC" / "report.pdf"
    second = tmp_path / "Company_APEX" / "report.pdf"
    saved = []

    monkeypatch.setattr(
        run_mistral_ocr,
        "extract_pdf",
        lambda pdf: Mock(pages=[Mock(index=0)]),
    )
    monkeypatch.setattr(
        run_mistral_ocr,
        "save_ocr_result",
        lambda result, pdf, output: saved.append((pdf, output)),
    )
    monkeypatch.setattr(sys, "argv", ["run_mistral_ocr", str(first), str(second)])

    run_mistral_ocr.main()

    assert len(saved) == 2
    assert saved[0][1].parts[-2:] == ("Company_ABC", "report_ocr.json")
    assert saved[1][1].parts[-2:] == ("Company_APEX", "report_ocr.json")