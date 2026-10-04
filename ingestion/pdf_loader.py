import pymupdf
from models.schemas import Document


def load_pdf(file) -> list[Document]:
    documents = []

    # Read uploaded PDF bytes
    pdf_bytes = file.getvalue()

    # Open PDF from memory
    pdf = pymupdf.open(stream=pdf_bytes, filetype="pdf")

    # Extract text page by page
    for page_number, page in enumerate(pdf, start=1):
        text = page.get_text()

        if isinstance(text, str):
            text = text.strip()

            if text:
                documents.append(
                    Document(
                        text=text,
                        source=file.name,
                        file_type="pdf",
                        metadata={
                            "page": page_number
                        }
                    )
                )

    pdf.close() 

    return documents