from networkx import edges, maximum_flow, maximum_flow_value, strongly_connected_components
import generalized_geography as gg
from generalized_geography.solver.changeable_deg import make_flow_graph
from generalized_geography.types.bipartite import BipartiteNode

graph = gg.load_guel_graph()

result = gg.cdeg_classify_fast(graph)
unk_graph = result.pruned_graph
win, lose, loop = gg.split_nodes_by_type(result.type_map)
win = gg.nodes_in_pos(win, 0)
lose = gg.nodes_in_pos(lose, 0)
loop = gg.nodes_in_pos(loop, 0)

flow_graph = gg.make_flow_graph(unk_graph)

moves = [(u, v, data["num"])
         for u, v, data in unk_graph.edges(data=True) if u.pos == 1]

scc_list = list(strongly_connected_components(unk_graph))

# 노드 -> SCC 인덱스 맵 생성
node_to_scc = {}
for idx, scc in enumerate(scc_list):
    for node in scc:
        node_to_scc[node] = idx

for u, v, num in moves:
    # u,v가 동일한 강연결요소에 속하는지 확인
    if node_to_scc[u] != node_to_scc[v]:
        continue

    flow_num = maximum_flow_value(
        flow_graph, v, u)+1
    if num > flow_num:
        print(u.name, "->", v.name, num, flow_num)
