import os
import pandas as pd
from nxpd import nxpdParams, draw

from graphitty.graphitty import Graphitty

# HTTP log from http://ita.ee.lbl.gov/html/contrib/NASA-HTTP.html

FIXTURE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'nasa_jul95.csv'
)
TEST_GRAPH_OUTPUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'artifacts',
    'simple_graph.png'
)


def test_read_generate_graph():
    if os.path.isfile(TEST_GRAPH_OUTPUT):
        os.remove(TEST_GRAPH_OUTPUT)

    df = pd.read_csv(FIXTURE)
    g = Graphitty(
        df,
        id_col='ip',
        beahivour_col='url',
        ts_col='date')
    nx_graph = g.create_graph(min_edges=0)

    draw(nx_graph, TEST_GRAPH_OUTPUT, show=False)

    # some data is drawn
    assert os.path.isfile(TEST_GRAPH_OUTPUT)
    filesize = os.stat(TEST_GRAPH_OUTPUT).st_size
    assert filesize > 1000
