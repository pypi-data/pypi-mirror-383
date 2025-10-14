# xkcd-random

Drop in replacement for random module that forces the core random number function to return 4, 0.4, 4/6. The
specification is a bit ambiguous.

Uses the [xkcd-221 algorithm](https://xkcd.com/221/).

![Function Returns 4](https://imgs.xkcd.com/comics/random_number.png
"XKCD Random Number Generator")

[![tests](https://github.com/matthewdeanmartin/xkcd_random/actions/workflows/build.yml/badge.svg)
](https://github.com/matthewdeanmartin/xkcd_random/actions/workflows/tests.yml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/matthewdeanmartin/xkcd_random/main.svg)
](https://results.pre-commit.ci/latest/github/matthewdeanmartin/xkcd_random/main)
[![Downloads](https://img.shields.io/pypi/dm/xkcd-random)](https://pypistats.org/packages/xkcd-random-four)
[![Python Version](https://img.shields.io/pypi/pyversions/xkcd-random-four)
![Release](https://img.shields.io/pypi/v/xkcd-random-four)
](https://pypi.org/project/xkcd-random-four/)

(The name xkcd-random is too close to some pre-existing package, so it is now xkcd-random-four)

## Installation

`pip install xkcd-random`

## Usage

```python
import xkcd_random as random

print(random.randint(0, 10))
```

## Caveats

Some functions return something other than 4/6 or 4 because the random.random() function's results are manipulated
before being returned to the user.

APIs might return 4 or 4/6, I don't know I haven't really tested it that well. You guys sure are picky about what random
numbers you want. You know, here use this

```python
import random

random.randint = lambda x: int(input("role a die"))
```

## Implementation

`SimpleOverrideXKCDRandom` overrides 4 methods of Random() like the docstring suggests.

```python
from random import Random


class SimpleOverrideXKCDRandom(Random):
    def random(self) -> float: return float(4 / 6)

    def getrandbits(self, k: int) -> int: return 4

    def seed(self, *_): ...

    def setstate(self, _): return ()

    def getstate(self): ...
```

`xkcd_random` is a fork of python 3.13. You can actually use this sensibly, with "system" (real randomness) or
"xkcd" (it is 4.)

```python
import xkcd_random

random = xkcd_random.Random(core=xkcd_random.SystemCore())
```

or

```python
import os

os.environ["RANDOM_BACKEND"] = "system"
import xkcd_random as random
```

## License

This code is copied directly from the python 3.11 so
the [license is the same as CPython's](https://github.com/python/cpython/blob/3.13/LICENSE). Anything not covered
by the cpython license is covered by MIT.

## Prior Art and Similar Libraries

This list has an emphasis on "drop in replacements"

- [RandomSources](https://pypi.org/project/RandomSources/)
- [nonpseudorandom](https://pypi.org/project/nonpseudorandom/)
- [Pyewacket](https://pypi.org/project/Pyewacket/)
- [quantum-random](https://pypi.org/project/quantum-random/)
- [pycrypto](https://pypi.org/project/pycrypto/)

## Project Health & Info

| Metric            | Health                                                                                                                                                                                                            | Metric          | Info                                                                                                                                                                                                                      |
|:------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:----------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Tests             | [![Tests](https://github.com/matthewdeanmartin/xkcd_random/actions/workflows/build.yml/badge.svg)](https://github.com/matthewdeanmartin/xkcd_random/actions/workflows/build.yml)                                  | License         | [![License](https://img.shields.io/github/license/matthewdeanmartin/xkcd_random)](https://github.com/matthewdeanmartin/xkcd_random/blob/main/LICENSE.md)                                                                  |
| Coverage          | [![Codecov](https://codecov.io/gh/matthewdeanmartin/xkcd_random/branch/main/graph/badge.svg)](https://codecov.io/gh/matthewdeanmartin/xkcd_random)                                                                | PyPI            | [![PyPI](https://img.shields.io/pypi/v/xkcd-random-four)](https://pypi.org/project/xkcd-random-four/)                                                                                                                     |
| Lint / Pre-commit | [![pre-commit.ci status](https://results.pre-commit.ci/badge/github/matthewdeanmartin/xkcd_random/main.svg)](https://results.pre-commit.ci/latest/github/matthewdeanmartin/xkcd_random/main)                      | Python Versions | [![Python Version](https://img.shields.io/pypi/pyversions/xkcd-random-four)](https://pypi.org/project/xkcd-random-four/)                                                                                                  |
| Quality Gate      | [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=matthewdeanmartin_xkcd-random\&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=matthewdeanmartin_xkcd-random)    | Docs            | [![Docs](https://readthedocs.org/projects/xkcd-random/badge/?version=latest)](https://xkcd-random.readthedocs.io/en/latest/)                                                                                              |
| CI Build          | [![Build](https://github.com/matthewdeanmartin/xkcd_random/actions/workflows/build.yml/badge.svg)](https://github.com/matthewdeanmartin/xkcd_random/actions/workflows/build.yml)                                  | Downloads       | [![Downloads](https://static.pepy.tech/personalized-badge/xkcd-random-four?period=total\&units=international_system\&left_color=grey\&right_color=blue\&left_text=Downloads)](https://pepy.tech/project/xkcd-random-four) |
| Maintainability   | [![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=matthewdeanmartin_xkcd-random\&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=matthewdeanmartin_xkcd-random) | Last Commit     | ![Last Commit](https://img.shields.io/github/last-commit/matthewdeanmartin/xkcd_random)                                                                                                                                   |

| Category        | Health                                                                                               
|-----------------|------------------------------------------------------------------------------------------------------|
| **Open Issues** | ![GitHub issues](https://img.shields.io/github/issues/matthewdeanmartin/xkcd_random)                 |
| **Stars**       | ![GitHub Repo stars](https://img.shields.io/github/stars/matthewdeanmartin/xkcd_random?style=social) |


## Mastodon Rel

<a rel="me" href="https://mastodon.social/@mistersql">Mastodon</a>

[Mastodon](https://mastodon.social/@mistersql){rel=me}

[Mastodon](https://mastodon.social/@mistersql){:rel="me"}