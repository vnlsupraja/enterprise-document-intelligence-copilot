from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END

from rag.answer_generator import AnswerGenerator


# --------------------------------------------------
# Agent State
# --------------------------------------------------

class AgentState(TypedDict):
    question: str
    task_type: str
    search_results: list
    retrieval_confidence: float
    evidence_sufficient: bool
    draft_answer: str
    final_answer: str
    answer_status: str
    workflow_steps: list[str]


# --------------------------------------------------
# Enterprise Agent Workflow
# --------------------------------------------------

class EnterpriseAgentWorkflow:

    def __init__(
        self,
        vector_store,
        similarity_threshold: float = 0.30
    ):

        self.vector_store = vector_store

        self.similarity_threshold = (
            similarity_threshold
        )

        self.answer_generator = (
            AnswerGenerator()
        )

        self.graph = self._build_graph()


    # --------------------------------------------------
    # Planner
    # --------------------------------------------------

    def planner_node(
        self,
        state: AgentState
    ) -> AgentState:

        question = state[
            "question"
        ].lower()

        troubleshooting_terms = [
            "error",
            "fail",
            "failed",
            "failure",
            "reject",
            "rejected",
            "issue",
            "problem",
            "fix",
            "resolve",
            "missing",
            "invalid"
        ]

        comparison_terms = [
            "compare",
            "difference",
            "different",
            "versus",
            " vs "
        ]

        if any(
            term in question
            for term in troubleshooting_terms
        ):
            task_type = "troubleshooting"

        elif any(
            term in question
            for term in comparison_terms
        ):
            task_type = "comparison"

        else:
            task_type = "knowledge_query"

        steps = state.get(
            "workflow_steps",
            []
        )

        steps.append(
            f"Planner: classified query as "
            f"'{task_type}'."
        )

        return {
            **state,
            "task_type": task_type,
            "workflow_steps": steps
        }


    # --------------------------------------------------
    # Retriever
    # --------------------------------------------------

    def retriever_node(
        self,
        state: AgentState
    ) -> AgentState:

        results = self.vector_store.search(
            state["question"],
            top_k=8
        )

        if results:
            best_score = results[0]["score"]
        else:
            best_score = 0.0

        evidence_sufficient = (
            best_score
            >= self.similarity_threshold
        )

        steps = state.get(
            "workflow_steps",
            []
        )

        steps.append(
            "Retriever: searched FAISS and "
            f"retrieved {len(results)} chunk(s)."
        )

        steps.append(
            "Retriever: best similarity score "
            f"was {best_score:.4f}."
        )

        return {
            **state,
            "search_results": results,
            "retrieval_confidence": best_score,
            "evidence_sufficient": evidence_sufficient,
            "workflow_steps": steps
        }


    # --------------------------------------------------
    # Routing
    # --------------------------------------------------

    def route_after_retrieval(
        self,
        state: AgentState
    ) -> str:

        if state.get(
            "evidence_sufficient",
            False
        ):
            return "reasoner"

        return "insufficient_evidence"


    # --------------------------------------------------
    # Insufficient Evidence
    # --------------------------------------------------

    def insufficient_evidence_node(
    self,
    state: AgentState
    ) -> AgentState:

        answer = (
            "This question appears to be outside the scope "
            "of the uploaded documents."
        )

        steps = state.get(
            "workflow_steps",
            []
        )

        steps.append(
            "Guardrail: retrieval relevance was too low, "
            "so LLM generation was skipped."
        )

        return {
            **state,
            "draft_answer": answer,
            "final_answer": answer,
            "answer_status": "out_of_scope",
            "workflow_steps": steps
        }
    # Reasoner
    # --------------------------------------------------

    def reasoner_node(
        self,
        state: AgentState
    ) -> AgentState:

        answer = (
            self.answer_generator.generate_answer(
                state["question"],
                state["search_results"]
            )
        )

        steps = state.get(
            "workflow_steps",
            []
        )

        steps.append(
            "Reasoner: generated a draft answer "
            "using retrieved evidence."
        )

        return {
            **state,
            "draft_answer": answer,
            "workflow_steps": steps
        }


    # --------------------------------------------------
    # Validator
    # --------------------------------------------------

    def validator_node(
        self,
        state: AgentState
    ) -> AgentState:

        answer = state.get(
            "draft_answer",
            ""
        ).strip()

        results = state.get(
            "search_results",
            []
        )

        confidence = state.get(
            "retrieval_confidence",
            0.0
        )

        insufficient_phrases = [
            "could not find sufficient information",
            "not enough information",
            "not provided in the documents",
            "not available in the documents",
            "does not contain information",
            "documents do not contain",
            "cannot determine from the provided"
        ]

        answer_lower = answer.lower()

        unsupported = any(
            phrase in answer_lower
            for phrase in insufficient_phrases
        )

        if not answer:

            final_answer = (
                "I could not generate a reliable answer "
                "from the uploaded documents."
            )

            answer_status = "generation_failed"

            validation_message = (
                "Validator: rejected an empty response."
            )

        elif not results or confidence < self.similarity_threshold:

            final_answer = (
                "I could not find sufficient information "
                "in the uploaded documents to answer "
                "this question."
            )

            answer_status = "insufficient_evidence"

            validation_message = (
                "Validator: insufficient retrieval evidence; "
                "answer blocked."
            )

        elif unsupported:

            final_answer = answer

            answer_status = "insufficient_evidence"

            validation_message = (
                "Validator: model correctly identified that "
                "the retrieved documents do not support "
                "the requested information."
            )

        else:

            final_answer = answer

            answer_status = "grounded"

            validation_message = (
                "Validator: grounded answer accepted with "
                "supporting retrieved evidence."
            )

        steps = state.get(
            "workflow_steps",
            []
        )

        steps.append(
            validation_message
        )

        return {
            **state,
            "final_answer": final_answer,
            "answer_status": answer_status,
            "workflow_steps": steps
        }


    # --------------------------------------------------
    # Build LangGraph
    # --------------------------------------------------

    def _build_graph(self):

        workflow = StateGraph(AgentState)  # type: ignore[type-var]

        workflow.add_node(
            "planner",
            self.planner_node
        )

        workflow.add_node(
            "retriever",
            self.retriever_node
        )

        workflow.add_node(
            "reasoner",
            self.reasoner_node
        )

        workflow.add_node(
            "validator",
            self.validator_node
        )

        workflow.add_node(
            "insufficient_evidence",
            self.insufficient_evidence_node
        )

        workflow.add_edge(
            START,
            "planner"
        )

        workflow.add_edge(
            "planner",
            "retriever"
        )

        workflow.add_conditional_edges(
            "retriever",
            self.route_after_retrieval,
            {
                "reasoner": "reasoner",
                "insufficient_evidence":
                    "insufficient_evidence"
            }
        )

        workflow.add_edge(
            "reasoner",
            "validator"
        )

        workflow.add_edge(
            "validator",
            END
        )

        workflow.add_edge(
            "insufficient_evidence",
            END
        )

        return workflow.compile()


    # --------------------------------------------------
    # Public Run Method
    # --------------------------------------------------

    def run(
        self,
        question: str
    ):

        initial_state: AgentState = {
            "question": question,
            "task_type": "",
            "search_results": [],
            "retrieval_confidence": 0.0,
            "evidence_sufficient": False,
            "draft_answer": "",
            "final_answer": "",
            "answer_status": "",
            "workflow_steps": []
        }

        return self.graph.invoke(
            initial_state
        )