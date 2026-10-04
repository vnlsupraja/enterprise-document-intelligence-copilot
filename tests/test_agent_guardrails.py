from unittest.mock import MagicMock

from agents.workflow import AgentState, EnterpriseAgentWorkflow
from models.schemas import DocumentChunk
from vectorstore.faiss_store import SearchResult


def create_state() -> AgentState:
    return {
        "question": "Test question",
        "task_type": "knowledge_query",
        "search_results": [],
        "retrieval_confidence": 0.0,
        "evidence_sufficient": False,
        "draft_answer": "",
        "final_answer": "",
        "answer_status": "",
        "workflow_steps": [],
    }


def create_workflow():
    """
    Create workflow with a mocked vector store.

    This prevents these unit tests from depending on
    SentenceTransformer, FAISS, or Gemini.
    """
    vector_store = MagicMock()

    workflow = EnterpriseAgentWorkflow(
        vector_store=vector_store,
        similarity_threshold=0.30,
    )

    return workflow, vector_store


def test_low_confidence_routes_to_insufficient_evidence():

    workflow, _ = create_workflow()

    state = create_state()

    state["retrieval_confidence"] = 0.05
    state["evidence_sufficient"] = False

    route = workflow.route_after_retrieval(state)

    assert route == "insufficient_evidence"


def test_supported_evidence_routes_to_reasoner():

    workflow, _ = create_workflow()

    state = create_state()

    state["retrieval_confidence"] = 0.75
    state["evidence_sufficient"] = True

    route = workflow.route_after_retrieval(state)

    assert route == "reasoner"


def test_insufficient_evidence_node_marks_out_of_scope():

    workflow, _ = create_workflow()

    state = create_state()

    state["question"] = "What is the capital of India?"
    state["retrieval_confidence"] = 0.01
    state["evidence_sufficient"] = False

    result = workflow.insufficient_evidence_node(
        state
    )

    assert result["answer_status"] == "out_of_scope"

    assert "outside the scope" in (
        result["final_answer"].lower()
    )

    assert result["draft_answer"] == result["final_answer"]

    assert any(
        "generation was skipped" in step.lower()
        for step in result["workflow_steps"]
    )


def test_retriever_low_score_blocks_reasoning():

    workflow, vector_store = create_workflow()

    chunk = DocumentChunk(
        text=(
            "The BEG03 element contains the "
            "purchase order number."
        ),
        source="test_document.pdf",
        file_type="pdf",
        chunk_id="test_1",
        metadata={"page": 1},
    )

    vector_store.search.return_value = [
        SearchResult(
            chunk=chunk,
            score=0.05,
        )
    ]

    state = create_state()

    state["question"] = "What is the capital of India?"

    result = workflow.retriever_node(state)

    assert result["retrieval_confidence"] == 0.05
    assert result["evidence_sufficient"] is False

    route = workflow.route_after_retrieval(result)

    assert route == "insufficient_evidence"