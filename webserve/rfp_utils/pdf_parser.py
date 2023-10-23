import pypdf

class PdfParser:

    def extract_text(self, file_handle):
        reader = pypdf.PdfReader("../samples/RFP/NewBrunswick/DIGITAL TRANSFORMATION SNB.CA.pdf")
        text = [p.get_text() for p in reader.pages]