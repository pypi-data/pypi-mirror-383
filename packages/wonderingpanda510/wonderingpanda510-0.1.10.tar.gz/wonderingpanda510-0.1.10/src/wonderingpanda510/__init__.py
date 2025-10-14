from wonderingpanda510._core import hello_from_bin
from . import differential, matrix, distributions	
from .matrix import rowswap, rowscale, rowreplacement, rref
from .distributions import exponentialdist, poissiondist
from .model import LinearRegression

__all__ = ["hello", "differential", "matrix", "distributions",
           "rowswap", "rowscale", "rowreplacement", "rref", "poissiondist", "exponentialdist",
           "LinearRegression"]

def hello() -> str:
    return hello_from_bin()
