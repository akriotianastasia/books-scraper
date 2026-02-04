from io import BytesIO
import pandas as pd

def books_to_excel_bytes(books: list[dict]) -> BytesIO:
    df = pd.DataFrame(books)
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="books")
    buf.seek(0)
    return buf
