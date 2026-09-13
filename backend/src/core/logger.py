import logging
import sys
import time

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True,
)

def get_logger(name: str):
    return logging.getLogger(name)

class Timer:
    def __init__(self, name: str):
        self.name = name
        self.start = time.time()
        self.log = get_logger(name)
    def end(self, extra=""):
        elapsed = time.time() - self.start
        self.log.info(f"{self.name} - {elapsed:.2f}s {extra}")
        return elapsed
