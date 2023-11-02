from io import BytesIO
from bs4 import BeautifulSoup

import pypdf
from pdfminer.high_level import extract_text_to_fp


class PdfParser:

    def extract_text(self, file_like):
        reader = pypdf.PdfReader(file_like)
        text = [p.extract_text() for p in reader.pages]
        
        return {
            'content': text,
            'format': 'list_str'
        }


class PdfHtmlParser:

    def extract_text(self, file_like):
        output = BytesIO()
        extract_text_to_fp(file_like, output, output_type='html')
        output.seek(0)

        return {
            'content': output.getvalue().decode('utf-8'),
            'format': 'html'
        }

    def parse_to_dom(self, pdf_text : str) -> BeautifulSoup:
        return BeautifulSoup(pdf_text, 'xml')
    
    def clean_xml(self, dom : BeautifulSoup) -> str:
        """run a visitor to clean the dom."""
        pass
