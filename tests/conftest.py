import os
import pytest

import pandas as pd

from graphitty.graphitty import Graphitty

ARTIFACTS_DIR = os.environ.get(
    'CIRCLE_ARTIFACTS',
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'artifacts',
    ))

# HTTP log from http://ita.ee.lbl.gov/html/contrib/NASA-HTTP.html
FIXTURE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'nasa_jul95.csv'
)


FIXTURE2 = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'nasa_aug95.csv'
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


@pytest.fixture
def g2():
    df = pd.read_csv(FIXTURE2)
    g = Graphitty(
        df,
        id_col='ip',
        beahivour_col='url',
        ts_col='date')
    return g
