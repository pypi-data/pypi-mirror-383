from typing import List
import hgtk
from networkx import DiGraph
from generalized_geography.common.utils import nodes_in_pos, split_nodes_by_type
from generalized_geography.datasets.oldict import load_oldict_words
from generalized_geography.solver.changeable_deg import cdeg_classify_fast
from generalized_geography.types.bipartite import BipartiteNode


def std(char: str):
    cho, jung, jong = hgtk.letter.decompose(char)
    if cho == "ㄹ" and jung in ["ㅑ", "ㅕ", "ㅛ", "ㅠ", "ㅣ", "ㅖ"]:
        return [char, hgtk.letter.compose("ㅇ", jung, jong)]

    elif cho == "ㄹ" and jung in ["ㅏ", "ㅐ", "ㅗ", "ㅜ", "ㅡ", "ㅚ"]:
        return [char, hgtk.letter.compose("ㄴ", jung, jong)]

    elif cho == "ㄴ" and jung in ["ㅕ", "ㅛ", "ㅠ", "ㅣ"]:
        return [char, hgtk.letter.compose("ㅇ", jung, jong)]

    else:
        return [char]


def words_to_graph(words: List[str]) -> DiGraph:

    g = DiGraph()
    for word in words:
        start_node = BipartiteNode(word[0], 1)
        end_node = BipartiteNode(word[-1], 0)
        if g.has_edge(start_node, end_node):
            g[start_node][end_node]["num"] += 1
        else:
            g.add_edge(start_node, end_node, num=1)

    for node in g.nodes:
        if node.pos == 0:

            for changeable in std(node.name):

                if BipartiteNode(changeable, 1) not in g.nodes:
                    continue

                next_node = BipartiteNode(changeable, 1)
                g.add_edge(node, next_node)

    return g

def load_guel_graph():
    words = load_oldict_words()
    graph = words_to_graph(words)
    return graph


