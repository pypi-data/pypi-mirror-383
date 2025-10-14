import generalized_geography as gg
import networkx as nx


graph = nx.DiGraph()
graph.add_edges_from([(1, 2, {"num": 2}), (2, 3, {"num": 5}), (3, 1, {
                     "num": 1}), (3, 4, {"num": 1}), (4, 4, {"num": 5})])
result = gg.deg_classify_fast(graph)
lose, win = gg.split_nodes_by_resolved_type(result.type_map)
print("Lose nodes:", lose)
print("Win nodes:", win)
print("Unknown nodes:", result.pruned_graph.nodes)
type_map = gg.deg_classify_complete(graph)
print()
print("After complete classification:")
lose, win = gg.split_nodes_by_resolved_type(type_map)
print("Lose nodes:", lose)
print("Win nodes:", win)
