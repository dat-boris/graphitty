"""
Test function with collapsing multiple graphs
"""
import os
from itertools import chain
from nxpd import draw

from .conftest import ARTIFACTS_DIR


def test_name_collapse(g, g2):
    # given 2 different graph, calculate the naming collapse
    nx_graph, name_mapping = g.shorten_name()
    output_png = os.path.join(
        ARTIFACTS_DIR,
        'name_shortened.png'
    )
    draw(nx_graph, output_png, show=False)
    _, name_mapping2 = g2.shorten_name()

    assert 5 <= len(name_mapping) <= 10

    # let's check that the name converge (nothing exotically different)
    def get_node_names(mapping):
        return set(mapping.keys())

    same = get_node_names(name_mapping) & get_node_names(name_mapping2)
    different = get_node_names(name_mapping) ^ get_node_names(name_mapping2)
    # print same
    # print different
    assert len(same) >= 3
    assert len(different) < 15



def xxtest_combine_graph(g, g2):
    # given 2 differnet graphs, shorten name and combine
    nx_combined = GraphCombiner(g, g2)
    output_png = os.path.join(
        ARTIFACTS_DIR,
        'combined.png'
    )
    draw(nx_graph, output_png, show=False)


def xxtest_comparison(g, g2):
    # overlay plotting on graph?
    # given 2 differnet graphs, shorten name and combine
    nx_combined = GraphCombiner(g, g2)

    comparisons = nx_combined.compare(image_folder=ARTIFACTS_DIR)
    # return a list of comparison, with a list of graphs
    assert len(comparison) > 3

    nx_combined.add_comparison_graph(signficance=0.03)

    output_png = os.path.join(
        ARTIFACTS_DIR,
        'combined.png'
    )
    draw(nx_graph, output_png, show=False)
