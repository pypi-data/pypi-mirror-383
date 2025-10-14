from matplotlib import pyplot as plt
from networkx.algorithms.cycles import simple_cycles
from networkx import DiGraph, draw, find_cycle
import generalized_geography as gg
import networkx as nx
import random

n = 5  # 노드 개수
G = nx.complete_graph(n)

# 방향 그래프로 변환
DG = nx.DiGraph()
DG.add_nodes_from(G.nodes())


# ✅ 짝수 사이클 강제로 하나 추가 (예: 0 → 1 → 2 → 3 → 0, 길이 4)
even_cycle_nodes = [0, 1, 2, 3]  # 길이 4 (짝수)
for i in range(len(even_cycle_nodes)):
    u = even_cycle_nodes[i]
    v = even_cycle_nodes[(i + 1) % len(even_cycle_nodes)]
    DG.add_edge(u, v, num=random.randint(1, 3))  # 방향 강제 지정

# 각 간선마다 무작위 방향 지정
for u, v in G.edges():
    if DG.has_edge(u, v) or DG.has_edge(v, u):
        continue  # 이미 간선이 추가된 경우 건너뜀
    if random.random() < 0.5:
        DG.add_edge(u, v, num=random.randint(1, 3))
    else:
        DG.add_edge(v, u, num=random.randint(1, 3))


# 이제 짝수 사이클을 찾음
cycle = [(v, even_cycle_nodes[(i + 1) % len(even_cycle_nodes)])
         for i, v in enumerate(even_cycle_nodes)]

# 혹시 find_cycle이 홀수 사이클을 반환하면,
# 짝수 사이클만 필터링


# ------------------------------------------------
# 이후 부분 동일
increase_limit = 100
print("cycle:", [u for u in cycle])
for i in range(increase_limit):
    for u, v in cycle:
        DG[u][v]['num'] = i
    type_map = gg.deg_classify_complete(DG)

    print("iteration:", i, "type_map:", "".join(
        [str(type_map[j]) for j in range(n)]))
