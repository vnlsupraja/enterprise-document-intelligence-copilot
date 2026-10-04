from pathlib import Path
from io import BytesIO

from ingestion.pdf_loader import load_pdf
from ingestion.txt_loader import load_txt
from ingestion.csv_loader import load_csv
from ingestion.excel_loader import load_excel


SAMPLE_DIR = Path(__file__).parent.parent / "data" / "sample_documents"


class MockUploadedFile(BytesIO):
    """
    Mimics the important behaviour of Streamlit UploadedFile.
    Our production loaders use file.getvalue().
    """

    def __init__(self, path: Path):
        self.path = path
        super().__init__(path.read_bytes())

        self.name = path.name
        self.type = self._get_mime_type()

    def _get_mime_type(self):
        mime_types = {
            ".pdf": "application/pdf",
            ".txt": "text/plain",
            ".csv": "text/csv",
            ".xlsx":
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }

        return mime_types.get(
            self.path.suffix.lower(),
            "application/octet-stream",
        )


def uploaded_file(filename):
    path = SAMPLE_DIR / filename

    assert path.exists(), f"Sample file not found: {path}"

    return MockUploadedFile(path)


def test_pdf_loader():
    file = uploaded_file("EDI_850_Implementation_Guide.pdf")

    documents = load_pdf(file)

    assert documents
    assert len(documents) > 0

    combined_text = " ".join(
        document.text
        for document in documents
    )

    assert "BEG" in combined_text


def test_txt_loader():
    file = uploaded_file("edi_incident_runbook.txt")

    documents = load_txt(file)

    assert documents
    assert len(documents) > 0

    combined_text = " ".join(
        document.text
        for document in documents
    )

    assert "E101" in combined_text
    assert "EDI Support Team" in combined_text


def test_csv_loader():
    file = uploaded_file("edi_transaction_errors.csv")

    documents = load_csv(file)

    assert documents
    assert len(documents) > 0

    combined_text = " ".join(
        document.text
        for document in documents
    )

    assert "TXN1001" in combined_text
    assert "Partner A" in combined_text
    assert "E101" in combined_text


def test_excel_loader():
    file = uploaded_file("edi_partner_performance.xlsx")

    documents = load_excel(file)

    assert documents
    assert len(documents) > 0

    combined_text = " ".join(
        document.text
        for document in documents
    )

    assert "Partner D" in combined_text