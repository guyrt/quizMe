import bs4

from dataclasses import dataclass

from typing import Iterable, List

@dataclass
class Chunk:
    content : str
    reason : str

    def __len__(self):
        return len(self.content)

    def __str__(self) -> str:
        return self.content


class RecursiveHtmlChunker:
    """Chunker that respects common HTML patterns.
    
    Aims for XXX length chunks.
    """

    def __init__(self) -> None:
        self._max_chunk_length = 1600  # 1600 characters
        self._min_chunk_length = 400 # min length we'll accept. Note that headers and other special elements may be shorter (but we may collapse them)
        pass

    def parse(self, dom : bs4.BeautifulSoup) -> List[Chunk]:
        """
        Enter the recursion then do post-process
        
        Invokes recursive HTML parser, which returns a list of Chunks or strings.
        The we must do two things:
        1. Assign every text element to a chunk.
        2. Break or consolidate chunks that are too big. 
        """
        maybe_chunks = self._recurse(dom)
        return self._consolidate_chunks(maybe_chunks)

    def _recurse(self, dom : bs4.element.PageElement) -> List[Chunk | str]:
        if isinstance(dom, bs4.Comment):
            return []
        if isinstance(dom, bs4.NavigableString):
            return [dom.text.strip()]
        if isinstance(dom, bs4.Tag) and dom.name == 'a':
            # return text only.
            return [dom.text.strip()]
        if isinstance(dom, bs4.Tag) and dom.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            return [Chunk(content=dom.text.strip(), reason='header')]
        
        # non base-conditions.
        if isinstance(dom, bs4.Tag) and dom.name in ['div', 'p', 'ul']:
            # consider doing li not ul
            children = self._invoke_on_children(dom.children)

            total_length = sum((len(c) for c in children))
            if total_length > self._max_chunk_length:
                return children
            
            inner_content = "\n".join([str(s) for s in children])
            if total_length > self._min_chunk_length:
                return [Chunk(content=inner_content, reason=dom.name)]
            else:
                # short content - prefer to return just a string.
                return [inner_content]

        return self._invoke_on_children(dom.children)

    def _invoke_on_children(self, children : Iterable[bs4.PageElement]):
        # helper
        children_results = []
        for d in children:
            e = self._recurse(d)
            if len(e) > 0:
                children_results.extend([ee for ee in e if ee])  # will eliminate empty elements
        return children_results

    def _consolidate_chunks(self, maybe_chunks : List[Chunk | str]) -> List[Chunk]:
        final_chunks : List[Chunk] = []

        # pass 1: consolidate
        consecutive_strings : List[str] = []
        for obj in maybe_chunks:
            if isinstance(obj, Chunk):
                # merge in all remaining chunks
                final_chunks.extend(self._merge_strings(consecutive_strings))
                consecutive_strings.clear()

                # append this chunk
                final_chunks.append(obj)
            else:
                consecutive_strings.append(obj)

        # if ended on strings need to merge what remains
        if len(consecutive_strings) > 0:
            final_chunks.extend(self._merge_strings(consecutive_strings))

        # pass 2: merge any remaining strings to nearest neighbor if possible.
        # if one side of relationship is header use other side. If both are headers create chunks.
        # if both sides non-header either merge to shorter (easy!) or merge based on embedding nearness (harder!)
        
        # pass 3: merge any short chunks to a longer chunk as long as it's not a header. 
        # prefer even sized 

        return [Chunk(content=c, reason='default') if isinstance(c, str) else c for c in final_chunks]

    def _merge_strings(self, obs : List[str]) -> List[str | Chunk]:
        len_sum = sum((len(c) for c in obs))
        if len_sum < self._max_chunk_length:
            return [Chunk(" \n".join(obs), reason='merge')]
        
        # handle too long string - split by size and recurse.
        second_half = [] # will be in reverse order
        cum_sum = 0
        while obs:
            o = obs.pop()
            o_l = len(o)
            if cum_sum + o_l < len_sum / 2:
                second_half.append(o)
                cum_sum += o_l
            else:
                break

        # if obs has items and o is set then decide to add back to end or append to second_half
        if o_l + cum_sum > (len_sum - cum_sum) + o_l:
            # add to the first half
            obs.append(o)
        else:
            second_half.append(o)

        return_set = []
        return_set.extend(self._merge_strings(obs))
        second_half.reverse()
        return_set.extend(self._merge_strings(second_half))
        return return_set


if __name__ == "__main__":
    b = bs4.BeautifulSoup("<div><b>hi</b>by<i>e</i></div>")
    ch = RecursiveHtmlChunker()


    rs2 = ch.parse(b)
    print(rs2)