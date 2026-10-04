from models.schemas import DocumentChunk
from vectorstore.faiss_store import FAISSVectorStore


def create_test_chunks():

    return [
        DocumentChunk(
            text=(
                "E101 - Missing Purchase Order Number. "
                "The BEG03 element is missing from the EDI 850 transaction. "
                "Populate BEG03 with a valid purchase order number."
            ),
            source="edi_incident_runbook.txt",
            file_type="txt",
            chunk_id="txt_1",
            metadata={}
        ),

        DocumentChunk(
            text=(
                "Transaction TXN1001 belongs to Partner A. "
                "The transaction failed with error E101 "
                "and has a retry count of 2."
            ),
            source="edi_transaction_errors.csv",
            file_type="csv",
            chunk_id="csv_1",
            metadata={"row": 2}
        ),

        DocumentChunk(
            text=(
                "Partner D processed 1100 transactions "
                "and had 55 failed transactions."
            ),
            source="edi_partner_performance.xlsx",
            file_type="xlsx",
            chunk_id="xlsx_1",
            metadata={
                "sheet": "Partner_Performance"
            }
        ),

        DocumentChunk(
            text=(
                "The purchase order date in BEG05 "
                "must use the CCYYMMDD format."
            ),
            source="EDI_850_Implementation_Guide.pdf",
            file_type="pdf",
            chunk_id="pdf_1",
            metadata={"page": 4}
        ),
    ]


def build_test_store():

    store = FAISSVectorStore()

    chunks = create_test_chunks()

    store.build_index(chunks)

    return store


def test_retrieve_e101_information():

    store = build_test_store()

    results = store.search(
        "What causes a missing purchase order number?",
        top_k=2
    )

    assert results
    assert len(results) > 0

    combined_text = " ".join(
        result["chunk"].text
        for result in results
    )

    assert "E101" in combined_text
    assert "BEG03" in combined_text


def test_retrieve_transaction():

    store = build_test_store()

    results = store.search(
        "Which transaction is TXN1001?",
        top_k=2
    )

    assert results

    combined_text = " ".join(
        result["chunk"].text
        for result in results
    )

    assert "TXN1001" in combined_text
    assert "Partner A" in combined_text


def test_retrieve_excel_information():

    store = build_test_store()

    results = store.search(
        "Which partner has 55 failed transactions?",
        top_k=2
    )

    assert results

    combined_text = " ".join(
        result["chunk"].text
        for result in results
    )

    assert "Partner D" in combined_text
    assert "55" in combined_text


def test_retrieve_date_format():

    store = build_test_store()

    results = store.search(
        "What format should the purchase order date use?",
        top_k=2
    )

    assert results

    combined_text = " ".join(
        result["chunk"].text
        for result in results
    )

    assert "CCYYMMDD" in combined_text
    assert "BEG05" in combined_text