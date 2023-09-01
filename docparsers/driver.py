from docparsers.parser_base import parse_file
from extract_doc_maker import try_find_creating_software


class ParserDriver(object):

    def parse_single_file(local_path):
        dom = parse_file(local_path)