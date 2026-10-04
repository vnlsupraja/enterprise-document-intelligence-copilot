from ingestion.chunker import split_text


def test_short_text_creates_single_chunk():

    text = "This is a short EDI document."

    chunks = split_text(
        text,
        chunk_size=800,
        chunk_overlap=150
    )

    assert len(chunks) == 1
    assert chunks[0] == text


def test_long_text_creates_multiple_chunks():

    text = "EDI transaction processing. " * 200

    chunks = split_text(
        text,
        chunk_size=200,
        chunk_overlap=50
    )

    assert len(chunks) > 1

    for chunk in chunks:
        assert len(chunk) <= 200


def test_chunks_are_not_empty():

    text = "EDI purchase order processing. " * 100

    chunks = split_text(
        text,
        chunk_size=200,
        chunk_overlap=50
    )

    assert all(
        chunk.strip()
        for chunk in chunks
    )