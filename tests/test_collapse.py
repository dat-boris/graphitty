"""
Test function with collapsing multiple graphs
"""

from .conftest import ARTIFACTS_DIR


def xxxtest_name_collapse(g):
    # given 2 different graph, calculate the naming collapse
    nx_graph, name_mapping = g.shorten_name()
    output_png = os.path.join(
        ARTIFACTS_DIR,
        'name_shortened.png'
    )
    draw(nx_graph, output_png, show=False)

    assert 'start' in name_mapping
    assert 5 <= len(name_mapping) <= 10


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
