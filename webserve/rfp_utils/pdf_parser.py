import pypdf

from typing import List

class PdfParser:

    def extract_text(self, file_like) -> List[str]:
        reader = pypdf.PdfReader(file_like)
        text = [p.extract_text() for p in reader.pages]
        return text
