import bs4

from dataclasses import dataclass

from typing import Iterable, List, Literal, Union

import logging

logger = logging.getLogger("default")


TypeReason = Literal["headermerge", "header", "merge", "div", "p", "ul"]


@dataclass
class Chunk:
    content: str
    reason: TypeReason

    def __len__(self):
        return len(self.content)

    def __str__(self) -> str:
        return self.content

    def is_header(self):
        return self.reason in ("headermerge", "header")


class RecursiveHtmlChunker:
    """Chunker that respects common HTML patterns.

    Aims for self._max_chunk_length length chunks.
    """

    def __init__(self) -> None:
        self._max_chunk_length = 1000  # 1600 characters
        self._min_chunk_length = 400  # min length we'll accept. Note that headers and other special elements may be shorter (but we may collapse them)
        pass

    def parse(self, dom: bs4.BeautifulSoup) -> List[Chunk]:
        """
        Enter the recursion then do post-process

        Invokes recursive HTML parser, which returns a list of Chunks or strings.
        The we must do two things:
        1. Assign every text element to a chunk.
        2. Break or consolidate chunks that are too big.
        """
        maybe_chunks = self._non_recurse(dom)
        return self._consolidate_chunks(maybe_chunks)

    def _non_recurse(self, dom: bs4.Tag) -> List[Union[Chunk, str]]:
        """I asked GPT4 to rewrite recursive approach."""
        stack = [(dom, False)]  # Each element is a tuple: (node, processed_flag)
        max_stack_length = 1
        result = []

        while stack:
            node, processed = stack.pop()

            if processed:
                # Handle aggregated children's content for container tags
                if isinstance(node, bs4.Tag) and node.name in ["div", "p", "ul"]:
                    children_content = [
                        r for r in result if isinstance(r, (Chunk, str))
                    ]
                    total_length = sum(len(str(c)) for c in children_content)
                    if total_length > self._max_chunk_length:
                        continue

                    inner_content = "\n".join(str(s) for s in children_content).strip()
                    if total_length > self._min_chunk_length:
                        result = [Chunk(content=inner_content, reason=node.name)]
                    else:
                        result = [inner_content]
                continue

            if isinstance(node, bs4.Comment):
                continue
            elif isinstance(node, bs4.NavigableString):
                result.append(node.strip())
                continue
            elif isinstance(node, bs4.Tag):
                if node.name == "a":
                    result.append(node.text.strip())
                    continue
                elif node.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                    result.append(Chunk(content=node.text.strip(), reason="header"))
                    continue
                elif node.name in ["div", "p", "ul"]:
                    # Mark current node as processed but needs aggregation later
                    stack.append((node, True))
                    # Add children to stack
                    for child in reversed(list(node.children)):
                        stack.append((child, False))
                    continue

            # Default case: if it's another type of Tag, process its children
            if isinstance(node, bs4.Tag):
                for child in reversed(list(node.children)):
                    stack.append((child, False))

            max_stack_length = max(max_stack_length, len(stack))

        logger.info("Max stack length seen was %s", max_stack_length)
        return result

    # NOT USED
    def _recurse(self, dom: bs4.element.PageElement) -> List[Chunk | str]:
        if isinstance(dom, bs4.Comment):
            return []
        if isinstance(dom, bs4.NavigableString):
            return [dom.text.strip()]
        if isinstance(dom, bs4.Tag) and dom.name == "a":
            # return text only.
            return [dom.text.strip()]
        if isinstance(dom, bs4.Tag) and dom.name in [
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
        ]:
            return [Chunk(content=dom.text.strip(), reason="header")]

        # non base-conditions.
        if isinstance(dom, bs4.Tag) and dom.name in ["div", "p", "ul"]:
            # consider doing li not ul
            children = self._invoke_on_children(dom.children)

            total_length = sum((len(c) for c in children))
            if total_length > self._max_chunk_length:
                return children

            inner_content = "\n".join([str(s) for s in children]).strip()
            if total_length > self._min_chunk_length:
                return [Chunk(content=inner_content, reason=dom.name)]
            else:
                # short content - prefer to return just a string.
                return [inner_content]

        return self._invoke_on_children(dom.children)

    def _invoke_on_children(self, children: Iterable[bs4.PageElement]):
        # helper
        children_results = []
        for d in children:
            e = self._recurse(d)
            if len(e) > 0:
                children_results.extend(
                    [ee for ee in e if ee]
                )  # will eliminate empty elements
        return children_results

    def _consolidate_chunks(self, maybe_chunks: List[Chunk | str]) -> List[Chunk]:
        # clear empties.
        maybe_chunks = [c for c in maybe_chunks if len(c) > 0]

        chunks: List[Chunk] = [
            Chunk(content=c, reason="default") if isinstance(c, str) else c
            for c in maybe_chunks
        ]

        # pass 0: merge headers to the subsequent section. It's ok to ignore length here.
        chunks = self._merge_to_header(chunks)

        # pass 1: merge any short chunks to a longer chunk without merging headers.
        chunks = self._merge_strings_header_aware(chunks)

        return chunks

    def _merge_to_header(self, in_chunks: List[Chunk]) -> List[Chunk]:
        ret_chunks = []

        current_pool = []
        roll_sum = 0

        recent_header = None

        def flush_pool():
            nonlocal roll_sum
            new_reason = "headermerge" if recent_header is not None else "merge"
            ret_chunks.append(
                Chunk("\n".join(c.content for c in current_pool), reason=new_reason)
            )
            current_pool.clear()
            roll_sum = 0

        i = 0
        last_i = -1

        while i < len(in_chunks):
            # sanity check your while resolves
            assert i != last_i
            last_i - i

            chunk = in_chunks[i]
            if chunk.is_header():
                recent_header = chunk
                flush_pool()
                current_pool = [chunk]
                roll_sum += len(chunk)

            elif recent_header is not None:
                # in a current header

                if roll_sum + len(chunk) < self._max_chunk_length:
                    current_pool.append(chunk)
                    roll_sum += len(chunk)
                else:
                    # too long - flush
                    flush_pool()
                    ret_chunks.append(chunk)
            else:
                # not in a header.
                ret_chunks.append(chunk)
            i += 1

        # handle recent_header set and not set but non-empty pool.
        if len(current_pool) > 0:
            flush_pool()

        return ret_chunks

    def _merge_strings_header_aware(self, in_chunks: List[Chunk]) -> List[Chunk]:
        """Iterate through chunks breaking on headers. When you see a header, break and consolidate"""
        ret_chunks = []
        current_pool = []
        rolling_sum = 0
        recent_header = None

        def flush_pool():
            nonlocal rolling_sum
            new_reason = "headermerge" if recent_header is not None else "merge"
            ret_chunks.extend(self._merge_strings(current_pool, new_reason))
            current_pool.clear()
            rolling_sum = 0

        i = 0
        last_i = -1
        while i < len(in_chunks):
            # sanity check your while resolves
            assert i != last_i
            last_i = i

            chunk = in_chunks[i]
            if chunk.is_header():
                # header found - reset
                if len(current_pool) > 0:
                    flush_pool()

                recent_header = chunk
            else:
                current_pool.append(chunk)
                rolling_sum += len(chunk)

            i += 1

        if len(current_pool) > 0:
            flush_pool()

        return ret_chunks

    def _merge_strings(self, obs: List[Chunk], new_reason: TypeReason) -> List[Chunk]:
        # expects mergable chunks - so handle headers upstream.
        if len(obs) < 2:
            return obs

        len_sum = sum((len(c) for c in obs))
        if len_sum < self._max_chunk_length:
            return [Chunk("\n".join(c.content for c in obs), reason=new_reason)]

        # handle too long string - split by size and recurse.
        second_half = []  # will be in reverse order
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
        if cum_sum > sum(len(c) for c in obs):
            # add back to the first half
            obs.append(o)
        else:
            second_half.append(o)

        return_set = []
        return_set.extend(self._merge_strings(obs, new_reason))
        second_half.reverse()
        return_set.extend(self._merge_strings(second_half, new_reason))
        return return_set


if __name__ == "__main__":
    b = bs4.BeautifulSoup("<div><b>hi</b>by<i>e</i></div>")
    ch = RecursiveHtmlChunker()

    rs2 = ch.parse(b)
    print(rs2)
