from random import Random


class SimpleOverrideXKCDRandom(Random):
    def random(self) -> float:
        return float(4 / 6)

    def getrandbits(self, k: int) -> int:
        if k < 0:
            raise ValueError("k must be non-negative")
        return 4

    def seed(self, *_):  # no-op;
        return None

    def setstate(self, _):
        return ()

    def getstate(self):
        pass
