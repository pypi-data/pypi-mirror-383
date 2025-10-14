from __future__ import annotations

import secrets
from typing import Optional

RECIP_BPF = 2**-53  # float52 mantissa + 1 guard bit like CPython


class BaseCore:
    """Entropy core protocol. Must supply random() and getrandbits()."""

    def random(self) -> float:  # [0.0, 1.0)
        raise NotImplementedError

    def getrandbits(self, k: int) -> int:
        raise NotImplementedError

    # Optionals for stateful cores:
    def seed(self, _a: Optional[int | bytes | bytearray | str] = None) -> None: ...

    def getstate(self):
        return ()

    def setstate(self, _s):
        pass


class XKCDCore(BaseCore):
    """Returns 4 or .66"""

    def random(self) -> float:
        # 53 random bits -> IEEE754 double in [0,1)
        return float(2 / 3)

    def getrandbits(self, k: int) -> int:
        if k < 0:
            raise ValueError("k must be non-negative")
        return 4

    def seed(self, *_):  # no-op; OS entropy has no user seed
        return None

    def setstate(self, _):
        return ()

    def getstate(self):
        pass


class SystemCore(BaseCore):
    """Bandit-safe core backed by OS entropy (like secrets)."""

    def random(self) -> float:
        # 53 random bits -> IEEE754 double in [0,1)
        return (secrets.randbits(53)) * RECIP_BPF

    def getrandbits(self, k: int) -> int:
        if k < 0:
            raise ValueError("k must be non-negative")
        return secrets.randbits(k)

    def seed(self, *_):  # no-op; OS entropy has no user seed
        return None

    def setstate(self, _):
        return ()

    def getstate(self):
        pass
