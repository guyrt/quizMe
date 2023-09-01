from parser_base import parse_file
from extract_doc_maker import try_find_creating_software
from docparsertypes import ParsedDoc

class ParserDriver(object):

    def parse_single_file(self, local_path):

        doc_details = ParsedDoc()

        dom = parse_file(local_path)
        doc_details.doc_maker = try_find_creating_software(dom)

        if doc_details.doc_maker:
            print(doc_details.doc_maker)
        else:
            print("No maker")



if __name__ == "__main__":
    ParserDriver().parse_single_file("D:/tmp/dirty.html")
