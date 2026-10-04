def retrieve_context(
    vector_store,
    question: str,
    top_k: int = 4
):

    results = vector_store.search(
        question,
        top_k=top_k
    )

    return results