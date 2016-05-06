#!/usr/bin/env python

"""
Script for consuming given file into output image

graphitty_csv csv1 csv1 combine_output.png
"""
import sys

import pandas as pd
from graphitty.graphitty import Graphitty
from graphitty.combiner import GraphCombiner
from nxpd import draw


def run_simplication(csv):
    output_png = csv + '.png'
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
    draw_with_output(nx_orig, "original_" + output_png)

    nx_orig = g.create_graph(
        min_edges=0,
        filter_subgraph=True
    )
    draw_with_output(nx_orig, "simplified_" + output_png)

    nx_condense = g.simplify()
    draw_with_output(nx_condense, output_png)

    return g


def draw_with_output(g, f):
    print "Drawing: {}".format(f)
    draw(g, f, show=False)

if __name__ == '__main__':
    csv1 = sys.argv[1]
    csv2 = sys.argv[2]
    imgout = sys.argv[3]
    g1 = run_simplication(csv1)
    g2 = run_simplication(csv2)

    g = GraphCombiner(g1, g2)
    nx_combined = g.create_graph()
    draw_with_output(nx_combined, imgout)
