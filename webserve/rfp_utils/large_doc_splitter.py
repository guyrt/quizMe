from typing import List

from azurewrapper.openai_client import OpenAIClient


class LargeDocSplitter:

    def __init__(self, token_counter : OpenAIClient) -> None:
        self._token_counter = token_counter

    def split(self, content : str, max_tokens : float, min_size : float=0.9, overlap : float=1/5) -> List[str]:
        """Split string on newline. 
        
        For each section, count tokens.
        Run through sections and add to window. """
        final_chunks = []
        state = _State()
        window = _RunningWindow(max_tokens)

        content = content.split('\n')
        content_sizes = [self._token_counter.num_tokens_from_string(c) for c in content]
        for line, size in zip(content, content_sizes):
            if line == '###table###':
                state.enter_table()
                window.add('table omitted', 0)
            elif line == '###endtable###':
                state.leave_table()
            else:
                if state.state == state.TABLE:
                    pass # in table so ignore
                    # maybe a "table omitted"
                else:
                    window.add(line, size)
                    # if window is full then run a cut.
                    if window.sum > max_tokens * min_size:
                        chunk = window.roll(overlap)
                        final_chunks.append(chunk)
        
        last_chunk = window.drain()
        if last_chunk:
            final_chunks.append(last_chunk)

        return final_chunks


class _RunningWindow:

    def __init__(self, max_tokens) -> None:
        self._window = []
        self._token_window = []
        self._max_tokens = max_tokens
        self.sum = 0

    def add(self, string, num_tokens):
        self._window.append(string)
        self.sum += num_tokens
        self._token_window.append(num_tokens)

    def roll(self, ratio):
        content_chunks = '\n'.join(self._window)
        self.cut(ratio)
        return content_chunks
    
    def drain(self):
        return '\n'.join(self._window)

    def cut(self, ratio):
        """Keep maximum section to retain 'ratio' of the total tokens."""
        keep = []
        keep_sizes = []
        rolling_chunks = 0
        for chunk, size in reversed(list(zip(self._window, self._token_window))):
            if size + rolling_chunks > ratio * self._max_tokens:
                # do not keep chunk
                break
            else:
                rolling_chunks += size
                keep.append(chunk)
                keep_sizes.append(size)

        self._window = list(reversed(keep))
        self._token_window = list(reversed(keep_sizes))
        self.sum = rolling_chunks


class _State:

    TABLE = 'table'
    NORMAL = 'normal'

    state = NORMAL

    def enter_table(self):
        self.state = self.TABLE

    def leave_table(self):
        self.state = self.NORMAL
