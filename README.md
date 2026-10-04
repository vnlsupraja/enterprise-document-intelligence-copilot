# Enterprise Document Intelligence Copilot

**Agentic RAG for Enterprise Document Analysis, Grounded Question
Answering, and Operational Troubleshooting**

[Live
Demo](https://enterprise-document-intelligence-copilot-amhkzru5gpgxyfdnhetee.streamlit.app/)
· [GitHub
Repository](https://github.com/vnlsupraja/enterprise-document-intelligence-copilot)

Enterprise Document Intelligence Copilot is a deployed Agentic RAG
application that ingests **PDF, TXT, CSV, and XLSX** enterprise
documents, builds a semantic knowledge base using **Sentence
Transformers + FAISS**, and orchestrates a **LangGraph** workflow with
**Google Gemini** to produce grounded, source-aware answers.

Unlike a general-purpose chatbot, the system applies
retrieval-confidence and evidence guardrails so unsupported or unrelated
questions can be classified as **Insufficient Evidence** or **Out Of
Scope** instead of being answered from the LLM's general knowledge.

## Architecture Overview

![Enterprise Document Intelligence Copilot
Architecture](docs/Enterprise%20Document%20Intelligence%20Architecture.png)

## Key Features

-   Multi-format ingestion for PDF, TXT, CSV, and XLSX
-   Semantic chunking and Sentence Transformer embeddings
-   FAISS vector similarity search
-   Retrieval-Augmented Generation (RAG)
-   LangGraph-based Planner → Retriever → Reasoner → Validator workflow
-   Google Gemini grounded reasoning
-   Cross-document retrieval and troubleshooting
-   Source-aware answers and retrieval scores
-   Insufficient-evidence and out-of-scope guardrails
-   Multi-question Streamlit chat interface
-   Session-based vector-index caching
-   Document/chunk inspection and agent workflow traceability
-   Automated Pytest suite with **21 passing tests**
-   Deployed Streamlit application

## Architecture

``` text
                    Enterprise Documents
                PDF | TXT | CSV | XLSX
                          |
                          v
                Multi-Format Ingestion
                          |
                          v
                 Unified Document Model
                          |
                          v
                       Chunking
                          |
                          v
                Sentence Transformers
                          |
                          v
                    FAISS Vector DB
                          |
User Question ------------+
                          |
                          v
                   LangGraph Agent
                          |
                  Planner / Retriever
                          |
                          v
                       Evidence
                          |
                          v
                    Reasoner (Gemini)
                          |
                          v
                       Validator
                          |
             +------------+------------+
             |            |            |
             v            v            v
          Grounded    Insufficient   Out Of
           Answer       Evidence      Scope
```

## Agent Workflow

### 1. Planner

Analyzes the user's question and identifies the task type, such as
knowledge retrieval or troubleshooting.

### 2. Retriever

Searches the FAISS vector index for semantically relevant chunks and
calculates retrieval relevance.

### 3. Reasoner

When sufficient evidence exists, relevant context is supplied to Google
Gemini to generate an answer grounded in the uploaded documents.

### 4. Validator

Checks whether adequate supporting evidence exists before returning the
final response.

Possible response states:

-   **Grounded**
-   **Insufficient Evidence**
-   **Out Of Scope**

Out-of-scope questions can be blocked before unnecessary LLM generation.

## Example Cross-Document Reasoning

> For transaction TXN1001, explain the error and what action should be
> taken if retransmission continues to fail.

The system can combine transaction-specific information from structured
CSV data with error definitions, remediation guidance, and escalation
instructions from enterprise documentation before generating a grounded
response.

## Hallucination Guardrail

For an unrelated question such as:

> What is the capital of India?

the deployed application retrieves no sufficiently relevant enterprise
evidence and classifies the request as **Out Of Scope** rather than
allowing Gemini to answer from general knowledge.

This demonstrates a key enterprise-AI design principle: **prioritize
grounded organizational evidence over unrestricted model knowledge.**

## Technology Stack

  Layer                  Technology
  ---------------------- ---------------------------
  Programming Language   Python
  User Interface         Streamlit
  LLM                    Google Gemini
  Agent Orchestration    LangGraph
  Embeddings             Sentence Transformers
  Vector Search          FAISS
  PDF Processing         PyMuPDF
  Tabular Processing     Pandas / OpenPyXL
  Testing                Pytest
  Configuration          python-dotenv
  Version Control        Git / GitHub
  Deployment             Streamlit Community Cloud

## Supported Document Formats

  Format   Processing
  -------- ---------------------------------------
  PDF      Page-level text extraction
  TXT      Text extraction
  CSV      Row-aware structured extraction
  XLSX     Sheet/row-aware structured extraction

Metadata such as page, row, sheet, source file, and file type is
preserved where applicable for traceability.

## Application Demo

### Multi-Format Enterprise Document Intelligence

The application accepts PDF, TXT, CSV, and XLSX documents and builds a
unified semantic knowledge base.

![Document Upload](docs/01-document-upload.png)

### Grounded RAG Response

Answers are generated using retrieved evidence from the uploaded
enterprise documents.

![Grounded Answer](docs/02-grounded-answer.png)

### Cross-Document Troubleshooting

The agent can combine evidence retrieved from multiple enterprise
sources to answer operational troubleshooting questions.

![Cross-Document Reasoning](docs/03-cross-document-reasoning.png)

### Hallucination Guardrail

Questions unsupported by the uploaded knowledge base are rejected rather
than answered using Gemini's general knowledge.

![Out-of-Scope Guardrail](docs/04-out-of-scope-guardrail.png)

## Results

The completed portfolio application demonstrates:

-   End-to-end multi-format enterprise RAG
-   Semantic retrieval using local embeddings and FAISS
-   Explicit agent orchestration with LangGraph
-   Cross-document operational troubleshooting
-   Source-grounded Gemini responses
-   Retrieval-based knowledge-boundary enforcement
-   Explainable workflow and evidence inspection
-   Automated regression testing
-   Successful cloud deployment

**Validation status:** `21 passed`

## Project Structure

``` text
enterprise-document-intelligence-copilot/
├── agents/
│   └── workflow.py
├── embeddings/
│   └── embedding_service.py
├── ingestion/
│   ├── chunker.py
│   ├── csv_loader.py
│   ├── document_processor.py
│   ├── excel_loader.py
│   ├── pdf_loader.py
│   └── txt_loader.py
├── models/
│   └── schemas.py
├── rag/
│   ├── answer_generator.py
│   ├── prompts.py
│   └── retrieval.py
├── vectorstore/
│   └── faiss_store.py
├── data/
│   └── sample_documents/
├── tests/
│   ├── test_agent_guardrails.py
│   ├── test_chunking.py
│   ├── test_imports.py
│   ├── test_ingestion.py
│   └── test_retrieval.py
├── docs/
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Installation

### 1. Clone the repository

``` bash
git clone https://github.com/vnlsupraja/enterprise-document-intelligence-copilot.git
cd enterprise-document-intelligence-copilot
```

### 2. Create and activate a virtual environment

Windows:

``` bash
python -m venv myenv
myenv\Scripts\activate
```

### 3. Install dependencies

``` bash
python -m pip install -r requirements.txt
```

### 4. Configure Gemini

Create a `.env` file:

``` env
GEMINI_API_KEY=your_gemini_api_key
```

Never commit the `.env` file or API key to source control.

### 5. Run the application

``` bash
python -m streamlit run app.py
```

## Example Questions

-   **Knowledge Retrieval:** What format should the purchase order date
    use?
-   **Structured Data Retrieval:** Which Partner A transaction has error
    E101 and is still failed?
-   **Operational Troubleshooting:** When should an E101 incident be
    escalated?
-   **Cross-Document Reasoning:** For transaction TXN1001, explain the
    error and what action should be taken if retransmission continues to
    fail.
-   **Guardrail Test:** What is the capital of India?

The guardrail question should be classified as **Out Of Scope** rather
than answered using general LLM knowledge.

## Automated Testing

Run:

``` bash
python -m pytest -v
```

Current validated result:

``` text
21 passed
```

Tests cover:

-   Module/import integrity
-   PDF/TXT/CSV/XLSX ingestion
-   Text chunking
-   Semantic retrieval
-   Agent routing and guardrails

Guardrail unit tests use mocked dependencies where appropriate, avoiding
unnecessary Gemini API calls during normal automated testing.

## Design Decisions

### Why FAISS?

FAISS provides fast local vector similarity search without requiring an
external vector database.

### Why Sentence Transformers?

Local embeddings separate retrieval from generation and avoid
unnecessary LLM API calls during document indexing and semantic search.

### Why LangGraph?

LangGraph provides explicit orchestration of planning, retrieval,
reasoning, validation, and guardrail routing rather than implementing
the application as a single LLM call.

### Why retrieval guardrails?

A RAG application can still generate unsupported answers when retrieval
quality is poor. This project evaluates retrieval relevance and can stop
generation when the uploaded knowledge base does not provide sufficient
evidence.

## Current Scope and Future Enhancements

The current portfolio version focuses on local semantic indexing,
multi-format document intelligence, grounded RAG, agentic orchestration,
retrieval guardrails, explainable evidence, automated testing, and cloud
deployment.

Potential future enhancements include:

-   Persistent vector storage
-   Hybrid keyword + semantic search
-   Reranking
-   Query decomposition
-   Conversational-context improvements
-   User authentication
-   Cloud object storage
-   Observability and evaluation metrics
-   Role-based document access

## Use Case

The included demonstration dataset uses enterprise EDI operations and
troubleshooting as an example domain. The architecture itself is
domain-independent and can be applied to technical documentation,
operational runbooks, incident knowledge bases, policies and procedures,
analytical documents, support documentation, and enterprise knowledge
management.

## Portfolio Skills Demonstrated

**Python • Generative AI • Agentic AI • RAG • LangGraph • Gemini •
Vector Search • FAISS • Semantic Retrieval • Streamlit • Automated
Testing • Cloud Deployment**

## Links

-   **Live Application:**
    https://enterprise-document-intelligence-copilot-amhkzru5gpgxyfdnhetee.streamlit.app/
-   **Source Code:**
    https://github.com/vnlsupraja/enterprise-document-intelligence-copilot
