from datetime import datetime
import json
import os

from bs4 import BeautifulSoup

from azurewrapper.raw_doc_queue import AzureQueueManagerBase
from azurewrapper.raw_doc_handler import AzureRawDocsBlobHandler
from azurewrapper.parsed_doc_handler import AzureParsedDocsBlobHandler
from indexgen.localtypes import get_sec_entry_from_dict

from .default_parser import DefaultParser
from .docparsertypes import ParsedDoc
from .extract_doc_maker import try_find_creating_software
from .parser_base import parse_file, parse_contents
from .toppan_merrill_bridge import ToppanMerrillBridgeParser


class ParserDriver(object):

    def __init__(self, 
                 raw_doc_handler : AzureRawDocsBlobHandler, 
                 incoming_queue_manager : AzureQueueManagerBase,
                 parsed_doc_handler : AzureParsedDocsBlobHandler,
                 outgoing_queue_manager : AzureQueueManagerBase,
                 peek_mode=False) -> None:
        self._raw_doc_handler = raw_doc_handler
        self._incoming_queue_manager = incoming_queue_manager
        self._parsed_doc_handler = parsed_doc_handler
        self._outgoing_queue_manager = outgoing_queue_manager

        self._peek_mode = peek_mode

    def parse_from_queue(self):
        """
        You could make this a pattern around pop/maybe delete/write.
        """
        msg = self._incoming_queue_manager.pop_doc_parse_message(peek=self._peek_mode)
        remote_path = msg.content
        files_to_parse = self._get_files_from_remote_summary(remote_path)
        for file_url in files_to_parse:
            parse_details, content = self.parse_remote(file_url)
            self._parsed_doc_handler.upload_files(parse_details, content)
        
        if not self._peek_mode:
            self._incoming_queue_manager.delete_doc_parse_message(msg)

        self._outgoing_queue_manager.write_message(remote_path)

    def parse_local_file(self, local_path):
        dom = parse_file(local_path)
        return self.parse_dom(dom, 'localfile')

    def parse_remote(self, remote_file):
        content = self._raw_doc_handler.get_path(remote_file)
        return self.parse_dom(parse_contents(content), remote_file)

    def parse_dom(self, dom : BeautifulSoup, doc_id : str):
        doc_details = ParsedDoc(doc_id=doc_id, parse_date=str(datetime.utcnow()))
        doc_details.doc_maker = try_find_creating_software(dom)
        content = self._run_parser(dom, doc_details.doc_maker)
        return doc_details, content
        
    def _get_files_from_remote_summary(self, remote_path : str):
        path_part = os.path.dirname(remote_path)
        summary_file_contents = json.loads(self._raw_doc_handler.get_path(remote_path))
        summary = get_sec_entry_from_dict(summary_file_contents)
        htm_files = (x for x in summary.edgar_files if x.filename.endswith('htm'))
        return [os.path.join(path_part, h.filename) for h in htm_files]

    def _run_parser(self, dom, doc_maker):
        if doc_maker == "Toppan Merrill Bridge":
            content_list = ToppanMerrillBridgeParser().parse(dom)
        else:
            content_list = DefaultParser().parse(dom)

        # drop special chars
        content_list = [c.replace('\u200b', '').replace('\\xa0', ' ').replace('&#160;', '') for c in content_list]
        content_list = (c for c in content_list if c)
        
        return "\n".join(content_list)


if __name__ == "__main__":
    ParserDriver().parse_single_file("../samples/tm2325071d1_8k.htm")
