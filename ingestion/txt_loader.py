from models.schemas import Document


def load_txt(file) -> list[Document]:

    # Read uploaded text file
    content = file.getvalue()

    # Decode bytes into text
    text = content.decode("utf-8", errors="ignore").strip()

    if not text:
        return []

    return [
        Document(
            text=text,
            source=file.name,
            file_type="txt",
            metadata={}
        )
    ]