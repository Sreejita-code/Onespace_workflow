import io
from docx import Document as DocxDocument
from . import _try_json

def parse_docx(file_bytes: bytes) -> list[dict]:
    doc = DocxDocument(io.BytesIO(file_bytes))
    endpoints = []
    for table in doc.tables:
        for row in table.rows[1:]: # Skip header row
            cells = [c.text.strip() for c in row.cells]
            if len(cells) >= 2:
                endpoints.append({
                    "method":       cells[0].upper() if cells[0] else "GET",
                    "url":          cells[1],
                    "description":  cells[2] if len(cells) > 2 else "",
                    "request_body": _try_json(cells[3] if len(cells) > 3 else ""),
                    "response_body":_try_json(cells[4] if len(cells) > 4 else ""),
                })
    return endpoints