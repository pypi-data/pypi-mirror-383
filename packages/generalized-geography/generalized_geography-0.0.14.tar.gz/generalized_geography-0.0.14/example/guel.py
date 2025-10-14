import generalized_geography as gg

graph = gg.load_guel_graph()

result = gg.cdeg_classify_fast(graph)
unk_graph = result.pruned_graph
win, lose, loop = gg.split_nodes_by_type(result.type_map)
win = gg.nodes_in_pos(win, 0)
lose = gg.nodes_in_pos(lose, 0)
loop = gg.nodes_in_pos(loop, 0)

print(f"Win positions: {len(win)}")
print(f"Lose positions: {len(lose)}")
print(f"Loop positions: {len(loop)}")
print(f"Unknown positions: {len(gg.nodes_in_pos(unk_graph.nodes, 0))}")
