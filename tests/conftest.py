import os
import pytest

import pandas as pd

from graphitty.graphitty import Graphitty


# HTTP log from http://ita.ee.lbl.gov/html/contrib/NASA-HTTP.html

FIXTURE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'nasa_jul95.csv'
)


@pytest.fixture
def g():
    df = pd.read_csv(FIXTURE)
    g = Graphitty(
        df,
        id_col='ip',
        beahivour_col='url',
        ts_col='date')
    return g
