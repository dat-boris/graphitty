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
    combine_g = GraphCombiner(g, g2, split_weight=False)
    name_mapping = combine_g.get_simplify_mapping()

    g1_simplify = combine_g.remap_graph(g, name_mapping)
    g2_simplify = combine_g.remap_graph(g2, name_mapping)

    nx_graph1 = g1_simplify.render_graph()
    output_png = os.path.join(
        ARTIFACTS_DIR,
        'name_shortened_1.png'
    )
    draw(nx_graph1, output_png, show=False)
    assert 5 <= len(nx_graph1.nodes()) <= 25

    nx_graph2 = g2_simplify.render_graph()
    output_png2 = os.path.join(
        ARTIFACTS_DIR,
        'name_shortened_2.png'
    )
    draw(nx_graph2, output_png2, show=False)
    assert 5 <= len(nx_graph2.nodes()) <= 25

    # let's check that the name converge (nothing exotically different)
    def get_node_names(G):
        return set(nx.nodes(G))

    same = get_node_names(nx_graph1) & get_node_names(nx_graph2)
    different = get_node_names(nx_graph1) ^ get_node_names(nx_graph2)
    # print "same={}".format(same)
    # print "different={}".format(different)
    assert len(same) >= 3
    assert 1 <= len(different) <= 20


def test_simplify_comparison(g, g2):
    g = GraphCombiner(g, g2)
    simplified_g = g.get_simplifed_combine_graph()
    nx_combined = simplified_g.render_graph()
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
