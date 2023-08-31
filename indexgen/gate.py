import time


class Gate(object):

    def __init__(self, secs) -> None:
        self._sleep = secs
        self._last_sleep_end = None

    def __enter__(self):
        print("enter")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def gate(self):
        if self._last_sleep_end:
            # get time to sleep
            sleep_time = self._sleep - (time.time() - self._last_sleep_end)
        else:
            sleep_time = -1

        print(f"Sleep: {sleep_time}")

        if sleep_time > 0:
            time.sleep(sleep_time)
        self._last_sleep_end = time.time()
