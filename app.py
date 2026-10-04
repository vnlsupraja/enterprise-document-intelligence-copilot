import streamlit as st
from ingestion.document_processor import process_document
from ingestion.chunker import chunk_documents
from vectorstore.faiss_store import FAISSVectorStore
from agents.workflow import EnterpriseAgentWorkflow


def get_file_signature(uploaded_files):
    if not uploaded_files:
        return None

    return tuple(
        sorted(
            (
                file.name,
                file.size
            )
            for file in uploaded_files
        )
    )


# Configure application
st.set_page_config(
    page_title="Enterprise Document Intelligence Copilot",
    page_icon="🤖",
    layout="wide"
)

# --------------------------------------------------
# Session State Initialization
# --------------------------------------------------

if "documents" not in st.session_state:
    st.session_state.documents = []

if "chunks" not in st.session_state:
    st.session_state.chunks = []

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "agent" not in st.session_state:
    st.session_state.agent = None

if "processed_file_signature" not in st.session_state:
    st.session_state.processed_file_signature = None

if "messages" not in st.session_state:
    st.session_state.messages = []

# Application title
st.title("Enterprise Document Intelligence Copilot")
st.caption(
    "Agentic RAG • Multi-Format Knowledge Retrieval • "
    "Grounded Enterprise AI"
)
st.write(
    "Analyze enterprise documents, investigate operational issues, "
    "and retrieve grounded answers across PDF, TXT, CSV, and Excel."
)

st.divider()

# Document upload section
st.header("Upload Enterprise Documents")

uploaded_files = st.file_uploader(
    "Upload PDF, TXT, CSV, or Excel files",
    type=["pdf", "txt", "csv", "xlsx"],
    accept_multiple_files=True
)

all_documents = st.session_state.get("documents", [])
chunks = st.session_state.get("chunks", [])
vector_store: FAISSVectorStore | None = st.session_state.get("vector_store", None)
agent = st.session_state.get("agent", None)

# Display uploaded files
if uploaded_files:
    current_signature = get_file_signature(uploaded_files)
    files_changed = (
        current_signature
        != st.session_state.processed_file_signature
    )

    if uploaded_files and files_changed:
        st.session_state.messages = []

        with st.spinner(
            "Processing documents and building vector index..."
        ):
            all_documents = []
            for uploaded_file in uploaded_files:
                st.write(f"📄 {uploaded_file.name}")

                try:
                    documents = process_document(uploaded_file)
                    all_documents.extend(documents)
                    st.caption(
                        f"Extracted {len(documents)} document unit(s)"
                    )
                except Exception as error:
                    st.error(
                        f"Could not process {uploaded_file.name}: {error}"
                    )

            if all_documents:
                chunks = chunk_documents(all_documents)
                vector_store = FAISSVectorStore()
                vector_store.build_index(chunks)
                agent = EnterpriseAgentWorkflow(vector_store)

                st.session_state.documents = all_documents
                st.session_state.chunks = chunks
                st.session_state.vector_store = vector_store
                st.session_state.agent = agent
                st.session_state.processed_file_signature = current_signature

                st.success(
                    f"Knowledge base ready — "
                    f"{len(uploaded_files)} files, "
                    f"{len(all_documents)} document units, "
                    f"{len(chunks)} searchable chunks."
                )

    elif uploaded_files:
        all_documents = st.session_state.documents
        chunks = st.session_state.chunks
        vector_store = st.session_state.vector_store
        agent = st.session_state.agent
        st.caption(
            f"✓ Knowledge base active — "
            f"{len(uploaded_files)} files indexed"
        )

    if uploaded_files and all_documents:
        st.divider()

        st.subheader("Knowledge Base")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Files", len(uploaded_files))
        with col2:
            st.metric("Document Units", len(all_documents))
        with col3:
            st.metric("Searchable Chunks", len(chunks))
        with col4:
            st.metric("Vector Index", "Ready")

        with st.expander("Document Inspection", expanded=False):
            selected_file = st.selectbox(
                "Select a file to inspect",
                options=[file.name for file in uploaded_files]
            )

            if selected_file:
                file_documents = [
                    doc for doc in all_documents if doc.source == selected_file
                ]

                st.success(
                    f"📄 Displaying **{len(file_documents)}** document units from **{selected_file}**"
                )

                for doc in file_documents:
                    with st.expander(
                        f"📄 Unit {doc.metadata.get('page', 'N/A')} ({doc.file_type})",
                        expanded=False
                    ):
                        st.text(doc.text)
                        st.caption(f"Metadata: {doc.metadata}")

            with st.expander("Preview extracted content"):
                for index, document in enumerate(
                    all_documents[:10],
                    start=1
                ):
                    st.markdown(f"**Document Unit {index}**")
                    st.write(f"Source: {document.source}")
                    st.write(f"Type: {document.file_type}")
                    st.write(f"Metadata: {document.metadata}")
                    preview = document.text[:500]
                    st.text(preview)
                    st.divider()

            with st.expander("Preview searchable chunks"):
                for index, chunk in enumerate(
                    chunks[:10],
                    start=1
                ):
                    st.markdown(f"### Chunk {index}")
                    st.write(f"Chunk ID: {chunk.chunk_id}")
                    st.write(f"Source: {chunk.source}")
                    st.write(f"Metadata: {chunk.metadata}")
                    st.text(chunk.text)
                    st.divider()

else:
    st.session_state.documents = []
    st.session_state.chunks = []
    st.session_state.vector_store = None
    st.session_state.agent = None
    st.session_state.processed_file_signature = None

st.divider()

# Question section
st.header("Ask the AI Copilot")

if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant":
            if message.get("task_type"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(
                        "Task Type",
                        message["task_type"]
                        .replace("_", " ")
                        .title()
                    )
                with col2:
                    score = message.get("retrieval_score")
                    if score is not None:
                        st.metric(
                            "Top Similarity",
                            f"{score:.4f}"
                        )
                with col3:
                    status = message.get("answer_status", "Unknown")
                    st.metric(
                        "Answer Status",
                        status
                        .replace("_", " ")
                        .title()
                    )

                workflow_steps = message.get("workflow_steps", [])
                if workflow_steps:
                    with st.expander("View Agent Workflow", expanded=False):
                        for step_number, step in enumerate(workflow_steps, start=1):
                            st.write(f"{step_number}. {step}")

                search_results = message.get("search_results", [])
                if search_results and message.get("answer_status") == "grounded":
                    st.subheader("Sources")
                    displayed_sources = set()
                    source_count = 0
                    MAX_DISPLAYED_SOURCES = 4
                    for search_result in search_results:
                        if source_count >= MAX_DISPLAYED_SOURCES:
                            break
                        chunk = search_result["chunk"]
                        source = chunk.source
                        if "page" in chunk.metadata:
                            source += f" — Page {chunk.metadata['page']}"
                        elif "sheet" in chunk.metadata:
                            source += f" — Sheet {chunk.metadata['sheet']}"
                            if "row" in chunk.metadata:
                                source += f", Row {chunk.metadata['row']}"
                        elif "row" in chunk.metadata:
                            source += f" — Row {chunk.metadata['row']}"

                        if source not in displayed_sources:
                            st.write(f"• {source}")
                            displayed_sources.add(source)
                            source_count += 1

                if search_results:
                    with st.expander("View Retrieved Evidence"):
                        for rank, search_result in enumerate(search_results, start=1):
                            chunk = search_result["chunk"]
                            score = search_result["score"]

                            st.markdown(f"**Evidence {rank}**")
                            st.write(f"Similarity: {score:.4f}")
                            st.write(f"Source: {chunk.source}")
                            if "page" in chunk.metadata:
                                st.write(f"Page: {chunk.metadata['page']}")
                            st.write(chunk.text)
                            st.divider()

question = st.chat_input(
    "Ask a question about your uploaded documents..."
)

if question:
    if st.session_state.agent is None:
        st.warning(
            "Please upload documents before asking questions."
        )
    else:
        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )

        with st.chat_message("user"):
            st.markdown(question)

        try:
            with st.chat_message("assistant"):
                with st.spinner("Analyzing documents..."):
                    result = st.session_state.agent.run(question)

                answer = result.get(
                    "final_answer",
                    "Unable to generate an answer."
                )

                task_type = result.get(
                    "task_type",
                    "unknown"
                )

                retrieval_score = result.get(
                    "retrieval_confidence",
                    result.get("retrieval_score")
                )

                answer_status = result.get(
                    "answer_status",
                    "unknown"
                )

                st.markdown(answer)

                if answer_status == "grounded":
                    st.success("Grounded in uploaded documents")
                elif answer_status == "insufficient_evidence":
                    st.warning(
                        "Relevant topic, but supporting evidence "
                        "was insufficient."
                    )
                elif answer_status == "out_of_scope":
                    st.info(
                        "Question is outside the scope of the "
                        "uploaded knowledge base."
                    )

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Task Type",
                        str(task_type).replace("_", " ").title()
                    )

                with col2:
                    if retrieval_score is not None:
                        st.metric(
                            "Top Similarity",
                            f"{retrieval_score:.4f}"
                        )

                with col3:
                    st.metric(
                        "Answer Status",
                        str(answer_status).replace("_", " ").title()
                    )

                workflow_steps = result.get("workflow_steps", [])
                if workflow_steps:
                    with st.expander("View Agent Workflow", expanded=False):
                        for step_number, step in enumerate(workflow_steps, start=1):
                            st.write(f"{step_number}. {step}")

                search_results = result.get("search_results", [])
                if search_results and result.get("answer_status") == "grounded":
                    st.subheader("Sources")
                    displayed_sources = set()
                    source_count = 0
                    MAX_DISPLAYED_SOURCES = 4
                    for search_result in search_results:
                        if source_count >= MAX_DISPLAYED_SOURCES:
                            break
                        chunk = search_result["chunk"]
                        source = chunk.source

                        if "page" in chunk.metadata:
                            source += f" — Page {chunk.metadata['page']}"
                        elif "sheet" in chunk.metadata:
                            source += f" — Sheet {chunk.metadata['sheet']}"
                            if "row" in chunk.metadata:
                                source += f", Row {chunk.metadata['row']}"
                        elif "row" in chunk.metadata:
                            source += f" — Row {chunk.metadata['row']}"

                        if source not in displayed_sources:
                            st.write(f"• {source}")
                            displayed_sources.add(source)
                            source_count += 1

                if search_results:
                    with st.expander("View Retrieved Evidence"):
                        for rank, search_result in enumerate(search_results, start=1):
                            chunk = search_result["chunk"]
                            score = search_result["score"]

                            st.markdown(f"**Evidence {rank}**")
                            st.write(f"Similarity: {score:.4f}")
                            st.write(f"Source: {chunk.source}")
                            if "page" in chunk.metadata:
                                st.write(f"Page: {chunk.metadata['page']}")
                            st.write(chunk.text)
                            st.divider()

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "task_type": task_type,
                    "retrieval_score": retrieval_score,
                    "answer_status": answer_status,
                    "workflow_steps": result.get("workflow_steps", []),
                    "search_results": result.get("search_results", [])
                }
            )

        except Exception as e:
            st.error(f"Unable to generate response: {e}")

st.divider()

# Sidebar
with st.sidebar:
    st.header("System Status")

    if st.session_state.vector_store is not None:
        st.success("Knowledge Base Ready")
        st.write("Document Ingestion: ✅")
        st.write("Vector Database: ✅")
        st.write("RAG Pipeline: ✅")
        st.write("AI Agent: ✅")
        st.write("Guardrails: ✅")
        st.divider()
        st.metric(
            "Indexed Files",
            len(uploaded_files) if uploaded_files else 0
        )
        st.metric(
            "Searchable Chunks",
            len(st.session_state.chunks)
        )
    else:
        st.info("Upload documents to initialize the knowledge base.")
        st.write("Document Ingestion: ○")

    st.caption("Powered by LangGraph • FAISS • Gemini")