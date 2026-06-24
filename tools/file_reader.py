from pathlib import Path
import json
import csv

import pdfplumber


def read_invoice(path: str) -> str:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"{path} does not exist.")

    extension = file_path.suffix.lower()

    if extension == ".txt":
        return file_path.read_text()

    if extension == ".json":
        with open(file_path) as f:
            return json.dumps(json.load(f))

    if extension == ".csv":
        rows = []

        with open(file_path) as f:
            reader = csv.reader(f)

            for row in reader:
                rows.append(",".join(row))

        return "\n".join(rows)

    if extension == ".pdf":
        text = ""

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

        return text

    raise ValueError(f"Unsupported file type: {extension}")