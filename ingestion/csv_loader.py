import io
import pandas as pd

from models.schemas import Document


def load_csv(file) -> list[Document]:

    # Read CSV into DataFrame
    dataframe = pd.read_csv(io.BytesIO(file.getvalue()))

    if dataframe.empty:
        return []

    documents = []

    # Convert each row into searchable text
    for row_number, (_, row) in enumerate(dataframe.iterrows(), start=2):

        row_text = " | ".join(
            f"{column}: {value}"
            for column, value in row.items()
        )

        documents.append(
            Document(
                text=row_text,
                source=file.name,
                file_type="csv",
                metadata={
                    "row": row_number
                }
            )
        )

    return documents