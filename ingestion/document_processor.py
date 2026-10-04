from ingestion.pdf_loader import load_pdf
from ingestion.txt_loader import load_txt
from ingestion.csv_loader import load_csv
from ingestion.excel_loader import load_excel


SUPPORTED_TYPES = {
    "pdf",
    "txt",
    "csv",
    "xlsx"
}


def process_document(file):

    # Detect file extension
    extension = file.name.rsplit(".", 1)[-1].lower()

    if extension not in SUPPORTED_TYPES:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    # Route file to correct loader
    if extension == "pdf":
        return load_pdf(file)

    if extension == "txt":
        return load_txt(file)

    if extension == "csv":
        return load_csv(file)

    if extension == "xlsx":
        return load_excel(file)

    return []