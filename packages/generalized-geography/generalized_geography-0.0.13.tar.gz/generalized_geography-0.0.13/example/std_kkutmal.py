from networkx import DiGraph
from generalized_geography.common.utils import split_nodes_by_type
from generalized_geography.datasets import load_oldict_words
import generalized_geography as gg

words = load_oldict_words()

g = DiGraph()
for word in words:
    start_node = word[0]
    end_node = word[-1]
    if g.has_edge(start_node, end_node):
        g[start_node][end_node]["num"] += 1
    else:
        g.add_edge(start_node, end_node, num=1)

result = gg.deg_classify_fast(g)
lose, win, loop = split_nodes_by_type(result.type_map)
print("Lose:", lose)
print("Win:", win)
print("Loop:", loop)

