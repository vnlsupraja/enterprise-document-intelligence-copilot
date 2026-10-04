import io
import pandas as pd

from models.schemas import Document


def load_excel(file) -> list[Document]:

    # Read all Excel sheets
    sheets = pd.read_excel(
        io.BytesIO(file.getvalue()),
        sheet_name=None
    )

    documents = []

    # Process every sheet
    for sheet_name, dataframe in sheets.items():

        if dataframe.empty:
            continue

        for row_number, (_, row) in enumerate(dataframe.iterrows(), start=2):

            row_text = " | ".join(
                f"{column}: {value}"
                for column, value in row.items()
            )

            documents.append(
                Document(
                    text=row_text,
                    source=file.name,
                    file_type="xlsx",
                    metadata={
                        "sheet": sheet_name,
                        "row": row_number
                    }
                )
            )

    return documents