import os
import pandas as pd
import networkx as nx
from nxpd import draw

from graphitty.graphitty import Graphitty
from .conftest import ARTIFACTS_DIR, FIXTURE


TEST_GRAPH_OUTPUT = os.path.join(
    ARTIFACTS_DIR,
    'simple_graph.png'
)


def test_read_generate_graph(g):
    if os.path.isfile(TEST_GRAPH_OUTPUT):
        os.remove(TEST_GRAPH_OUTPUT)

    nx_graph = g.render_graph(
        filter_subgraph=True
    )
    draw(nx_graph, TEST_GRAPH_OUTPUT, show=False)

    # some data is drawn
    assert os.path.isfile(TEST_GRAPH_OUTPUT)
    filesize = os.stat(TEST_GRAPH_OUTPUT).st_size
    assert filesize > 1000

    assert len(nx_graph.nodes()) > 5
    assert nx.number_connected_components(nx_graph.to_undirected()) == 1


def test_simplification(g):
    output_png = os.path.join(ARTIFACTS_DIR, 'tree.png')

    if os.path.isfile(output_png):
        os.remove(output_png)

    g_simplify = g.simplify()
    nx_tree = g_simplify.render_graph(
        filter_subgraph=True
    )
    draw(nx_tree, output_png, show=False)


def test_simplify_explicit_with_shorten(g):
    """
    Simplify using explicit mapping

    Simplify include:
    1. generate simplify mapping
    2. ensure the mapping output shorten name
    3. map to new node
    """
    output_png = os.path.join(ARTIFACTS_DIR, 'simplify_tree.png')

    mapping = g.get_simplify_mapping(shorten=True)
    assert 'start' in mapping.keys()

    # mapping = g.get_simplify_mapping(shorten=False)
    # assert '[1] start' in mapping.keys()

    df = pd.read_csv(FIXTURE)
    g_simplify = Graphitty(
        df,
        id_col='ip',
        beahivour_col='url',
        ts_col='date',
        node_mapping=mapping)
    assert 'start' in g_simplify.G.nodes()

    nx_tree = g_simplify.render_graph(
        filter_subgraph=True
    )
    draw(nx_tree, output_png, show=False)
