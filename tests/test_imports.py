def test_ingestion_modules_import():
    import ingestion.pdf_loader
    import ingestion.txt_loader
    import ingestion.csv_loader
    import ingestion.excel_loader
    import ingestion.document_processor
    import ingestion.chunker


def test_embedding_module_import():
    import embeddings.embedding_service


def test_vectorstore_module_import():
    import vectorstore.faiss_store


def test_rag_modules_import():
    import rag.retrieval
    import rag.answer_generator
    import rag.prompts


def test_agent_module_import():
    import agents.workflow


def test_schema_module_import():
    import models.schemas