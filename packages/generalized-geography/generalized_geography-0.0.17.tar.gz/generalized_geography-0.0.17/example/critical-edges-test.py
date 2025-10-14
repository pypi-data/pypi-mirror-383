
import generalized_geography as gg
from generalized_geography.types.bipartite import BipartiteNode


graph = gg.load_guel_graph()
graph.remove_edge(BipartiteNode("첩", 1), BipartiteNode("꽂", 0))
result = gg.cdeg_classify_fast(graph)
unk_graph = result.pruned_graph

win, lose, loop = gg.split_nodes_by_type(result.type_map)
win = gg.nodes_in_pos(win, 0)
lose = gg.nodes_in_pos(lose, 0)
loop = gg.nodes_in_pos(loop, 0)

critical_edges = gg.cdeg_get_critical_edges(unk_graph)
print("Critical edges:", "\n".join(
    sorted([u.name+v.name for u, v in critical_edges])))
