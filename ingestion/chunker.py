from models.schemas import Document, DocumentChunk


CHUNK_SIZE = 800
CHUNK_OVERLAP = 150


def split_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP
) -> list[str]:

    if not text:
        return []

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = start + chunk_size

        chunk = text[start:end]

        # Try to avoid cutting a sentence in the middle
        if end < text_length:

            last_period = chunk.rfind(".")
            last_newline = chunk.rfind("\n")

            split_position = max(
                last_period,
                last_newline
            )

            # Only use the natural boundary if it is
            # reasonably close to the end of the chunk.
            if split_position > chunk_size * 0.5:
                end = start + split_position + 1
                chunk = text[start:end]

        chunk = chunk.strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        # Create overlap between consecutive chunks
        new_start = end - chunk_overlap

        # Safety check
        if new_start <= start:
            new_start = end

        start = new_start

    return chunks


def chunk_documents(
    documents: list[Document]
) -> list[DocumentChunk]:

    all_chunks = []

    for document_index, document in enumerate(documents):

        text_chunks = split_text(document.text)

        for chunk_index, text in enumerate(text_chunks):

            chunk_id = (
                f"{document_index}_{chunk_index}"
            )

            metadata = document.metadata.copy()

            metadata["chunk_index"] = chunk_index

            all_chunks.append(
                DocumentChunk(
                    text=text,
                    source=document.source,
                    file_type=document.file_type,
                    chunk_id=chunk_id,
                    metadata=metadata
                )
            )

    return all_chunks