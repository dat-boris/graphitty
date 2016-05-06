"""
Test function with collapsing multiple graphs
"""
import os
from itertools import chain
import networkx as nx
from nxpd import draw

from graphitty.combiner import GraphCombiner

from .conftest import ARTIFACTS_DIR


def test_name_collapse(g, g2):
    name_mapping = g.shorten_name(simplify=False)
    nx_graph1 = g.render_graph()
    output_png = os.path.join(
        ARTIFACTS_DIR,
        'name_shortened.png'
    )
    draw(nx_graph1, output_png, show=False)
    name_mapping2 = g2.shorten_name(simplify=False)
    nx_graph2 = g.render_graph()

    assert 5 <= len(nx_graph1.nodes()) <= 25
    assert 5 <= len(nx_graph2.nodes()) <= 25

    # let's check that the name converge (nothing exotically different)
    def get_node_names(G):
        return set(nx.nodes(G))

    same = get_node_names(nx_graph1) & get_node_names(nx_graph2)
    different = get_node_names(nx_graph1) ^ get_node_names(nx_graph2)
    # print same
    # print different
    assert len(same) >= 3
    assert len(different) < 15


def test_combine_graph(g, g2, slow_runner=False):
    if slow_runner:
        g = GraphCombiner(g, g2, simplify=False)
        g.do_compare()
        nx_combined = g.render_graph()
        output_png = os.path.join(
            ARTIFACTS_DIR,
            'combined.png'
        )
        draw(nx_combined, output_png, show=False)

        assert 'start' in nx_combined.nodes()
        assert len(nx_combined.nodes()) <= 250


def test_simplify_comparison(g, g2):
    g = GraphCombiner(g, g2, simplify=True)
    g.do_compare()
    nx_combined = g.render_graph()
    output_png = os.path.join(
        ARTIFACTS_DIR,
        'simplify_combined.png'
    )
    draw(nx_combined, output_png, show=False)

    assert len(nx_combined.nodes()) < 25

    # comparisons = nx_combined.compare(image_folder=ARTIFACTS_DIR)
    # # return a list of comparison, with a list of graphs
    # assert len(comparison) > 3

    # nx_combined.add_comparison_graph(signficance=0.03)
