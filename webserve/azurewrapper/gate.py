import time


class Gate(object):
    def __init__(self, secs) -> None:
        self._sleep = secs
        self._last_sleep_end = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def gate(self):
        if self._last_sleep_end:
            # get time to sleep
            sleep_time = self._sleep - (time.time() - self._last_sleep_end)
        else:
            sleep_time = -1

        if sleep_time > 0:
            time.sleep(sleep_time)
        self._last_sleep_end = time.time()


if __name__ == "__main__":
    from datetime import datetime

    with Gate(1) as g:
        while True:
            g.gate()
            print(datetime.now())
