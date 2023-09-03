from parser_base import parse_file
from extract_doc_maker import try_find_creating_software
from docparsertypes import ParsedDoc

from default_parser import DefaultParser
from toppan_merrill_bridge import ToppanMerrillBridgeParser

class ParserDriver(object):

    def parse_single_file(self, local_path):

        doc_details = ParsedDoc()

        dom = parse_file(local_path)
        doc_details.doc_maker = try_find_creating_software(dom)
        content = self._run_parser(dom, doc_details.doc_maker)
        print(content)
        
    def _run_parser(self, dom, doc_maker):
        if doc_maker == "Toppan Merrill Bridge":
            content_list = ToppanMerrillBridgeParser().parse(dom)
        else:
            content_list = DefaultParser().parse(dom)
        import pdb; pdb.set_trace()
        # drop special chars
        content_list = [c.replace('\u200b', '').replace('\\xa0', ' ') for c in content_list]
        content_list = (c for c in content_list if c)
        
        return "\n".join(content_list)


if __name__ == "__main__":
    ParserDriver().parse_single_file("../samples/tm2325071d1_8k.htm")
