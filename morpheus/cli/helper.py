import numpy as np
import itertools

def chunk_into_n(lst, n):
    return list(map(lambda a: list(a), np.array_split(lst, n)))

def flatten(lst):
    return sum(lst, [])

def get_combinations(lengths: list[int]) -> list[tuple[int]]:
    rs = [range(v) for v in lengths]
    cs = list(itertools.product(*rs))
    return cs