#!/usr/bin/env python

"""
Script for consuming given file into output image
"""
import sys

import pandas as pd
from graphitty.graphitty import Graphitty
from nxpd import draw


def run_simplication(csv, output_png):
    df = pd.read_csv(csv)
    g = Graphitty(
        df,
        id_col='ip',
        beahivour_col='url',
        ts_col='date')

    # draw non-condensed version
    nx_orig = g.create_graph(
        min_edges=0,
        filter_subgraph=False
    )
    draw(nx_orig, "original_" + output_png, show=False)

    nx_orig = g.create_graph(
        min_edges=0,
        filter_subgraph=True
    )
    draw(nx_orig, "simplified_" + output_png, show=False)

    nx_condense = g.simplify()
    draw(nx_condense, output_png, show=False)


if __name__ == '__main__':
    run_simplication(sys.argv[1], sys.argv[2])
