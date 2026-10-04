import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors

from rag.prompts import SYSTEM_PROMPT

load_dotenv()


class AnswerGenerator:

    def __init__(self):
        api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY was not found. "
                "Add it to your .env file."
            )

        self.client = genai.Client(
            api_key=api_key
        )
        self.model_name = "gemini-3.5-flash-lite"

    def generate_answer(self, question: str, search_results: list) -> str:
        """Generate an answer using Gemini model.

        Args:
            question: The user's question.
            search_results: List of result dicts, each containing a 'chunk' with 'text' and optional metadata.

        Returns:
            A string answer.
        """
        if not search_results:
            return (
                "I could not find sufficient information "
                "in the uploaded documents to answer "
                "this question."
            )

        context_parts = []

        for result in search_results:
            chunk = result["chunk"]

            source_info = f"Source: {chunk.source}"

            if "page" in chunk.metadata:
                source_info += f", Page: {chunk.metadata['page']}"

            if "sheet" in chunk.metadata:
                source_info += f", Sheet: {chunk.metadata['sheet']}"

            if "row" in chunk.metadata:
                source_info += f", Row: {chunk.metadata['row']}"

            context_parts.append(
                f"""
{source_info}

Content:
{chunk.text}
"""
            )

        context = "\n---\n".join(context_parts)

        prompt = f"""
{SYSTEM_PROMPT}

DOCUMENT CONTEXT
================

{context}

USER QUESTION
==============

{question}

ANSWER
======

Answer the question using only the document context.
"""

        max_attempts = 3

        for attempt in range(max_attempts):

            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )

                if response.text:
                    return response.text

            except errors.ServerError as error:

                # Retry temporary Gemini server/capacity errors
                if error.code in (500, 503):

                    if attempt < max_attempts - 1:
                        wait_seconds = 2 ** attempt
                        time.sleep(wait_seconds)
                        continue

                    return (
                        "The AI reasoning service is temporarily busy. "
                        "The relevant document evidence was retrieved successfully, "
                        "but the generated answer is temporarily unavailable. "
                        "Please retry shortly."
                    )

                raise

        return (
            "The AI service did not return a response. "
            "Please retry the question."
        )