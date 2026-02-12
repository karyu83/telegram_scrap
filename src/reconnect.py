BASE_DELAY = 30
MAX_DELAY = 300


def calculate_backoff(attempt):
    delay = BASE_DELAY * (2 ** attempt)
    return min(delay, MAX_DELAY)


class ReconnectManager:
    def __init__(self, on_reconnect=None):
        self.attempt = 0
        self._on_reconnect = on_reconnect

    def get_delay(self):
        return calculate_backoff(self.attempt)

    def record_failure(self):
        self.attempt += 1

    def record_success(self):
        self.attempt = 0
        if self._on_reconnect:
            self._on_reconnect()


def extract_flood_wait_seconds(error):
    return error.seconds
