"""
Test function with collapsing multiple graphs
"""
import os
from itertools import chain
from nxpd import draw

from graphitty.combiner import GraphCombiner

from .conftest import ARTIFACTS_DIR


def test_name_collapse(g, g2):
    nx_graph, name_mapping = g.shorten_name()
    output_png = os.path.join(
        ARTIFACTS_DIR,
        'name_shortened.png'
    )
    draw(nx_graph, output_png, show=False)
    _, name_mapping2 = g2.shorten_name()

    assert 5 <= len(name_mapping) <= 13

    # let's check that the name converge (nothing exotically different)
    def get_node_names(mapping):
        return set(mapping.keys())

    same = get_node_names(name_mapping) & get_node_names(name_mapping2)
    different = get_node_names(name_mapping) ^ get_node_names(name_mapping2)
    # print same
    # print different
    assert len(same) >= 3
    assert len(different) < 15


def test_combine_graph(g, g2):
    g = GraphCombiner(g, g2)
    nx_combined = g.create_graph()
    output_png = os.path.join(
        ARTIFACTS_DIR,
        'combined.png'
    )
    draw(nx_combined, output_png, show=False)

    assert 'start' in nx_combined.nodes()
    assert 15 <= len(nx_combined.nodes()) <= 20


def test_simplify_comparison(g, g2):
    # g.simplify()
    # g2.simplify()

    g = GraphCombiner(g, g2, simplify=True)
    nx_combined = g.create_graph()

    output_png = os.path.join(
        ARTIFACTS_DIR,
        'simplify_combined.png'
    )
    draw(nx_combined, output_png, show=False)

    assert len(nx_combined.nodes()) < 16

    # comparisons = nx_combined.compare(image_folder=ARTIFACTS_DIR)
    # # return a list of comparison, with a list of graphs
    # assert len(comparison) > 3

    # nx_combined.add_comparison_graph(signficance=0.03)
