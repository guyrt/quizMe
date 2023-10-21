

class SP500Filter:

    def __init__(self) -> None:
        raw_list = open("intelligence/data/listed_cik.txt", 'r').read()
        lines = (s.strip().split('\t') for s in raw_list)
        self._cik_map = {_pad(s[1]): s[0] for s in lines}

    def filter(self, cik : str) -> bool:
        return cik in self._cik_map


def _pad(raw_cik : str) -> str:
    # 0000786947
    l = len(raw_cik)
    return '0' * (10 - l) + raw_cik
