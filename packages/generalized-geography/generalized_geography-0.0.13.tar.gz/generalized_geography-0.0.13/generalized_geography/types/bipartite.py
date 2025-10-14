from ast import Tuple
from typing import Hashable, NamedTuple


BipartiteNode = NamedTuple(
    "BipartiteNode", [("name", Hashable), ("pos", 0 | 1)])
