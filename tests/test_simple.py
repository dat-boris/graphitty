import os
import networkx as nx
from nxpd import draw

ARTIFACTS_DIR = os.environ.get(
    'CIRCLE_ARTIFACTS',
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'artifacts',
    ))


TEST_GRAPH_OUTPUT = os.path.join(
    ARTIFACTS_DIR,
    'simple_graph.png'
)


def test_read_generate_graph(g):
    if os.path.isfile(TEST_GRAPH_OUTPUT):
        os.remove(TEST_GRAPH_OUTPUT)

    nx_graph = g.create_graph(
        min_edges=0,
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

    g.create_graph(
        min_edges=0,
        filter_subgraph=True
    )
    nx_tree = g.simplify(min_edges=0)
    output_png = os.path.join(
        ARTIFACTS_DIR,
        'tree.png'
    )
    draw(nx_tree, output_png, show=False)
