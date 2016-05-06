"""
Combine multiple graphs into one

* Using shorten_name as key
* Compare edges using weight1, weight2
"""

from .graphitty import Graphitty
from .comparator import Comparator


class GraphCombiner(object):

    def __init__(self, g1, g2, simplify=False):
        self.G = self.combine_graph(g1, g2, simplify=simplify)

    def create_graph(self):
        return self.G

    @classmethod
    def combine_graph(cls,
                      g1, g2,
                      simplify=False):
        # 1. get shortname of g1
        nx1, _ = g1.shorten_name(simplify=simplify)
        nx2, _ = g2.shorten_name(simplify=simplify)

        nx1.add_nodes_from(nx2)
        # nx1.add_edges_from(nx2)
        edge_data = {}
        g1_edges = nx1.edges()
        total1 = 0
        total2 = 0
        for n1, n2 in g1_edges:
            weight = nx1.get_edge_data(n1, n2).get('weight', 0)
            nx1[n1][n2]['weight1'] = weight
            total1 += weight

        for n1, n2 in nx2.edges():
            weight = nx2.get_edge_data(n1, n2).get('weight', 0)
            if (n1, n2) in g1_edges:
                nx1[n1][n2]['weight2'] = weight
            else:
                nx1.add_edge(n1, n2,
                             weight2=weight)
            total2 += weight

        # now execute comparison
        for n1, n2 in nx1.edges():
            eattr = nx1.get_edge_data(n1, n2)
            nx1[n1][n2]['comparison'] = Comparator.compare_value(
                eattr.get('weight1', 0),
                eattr.get('weight2', 0),
                total1=total1,
                total2=total2
            )

        def render_func(G, edge, count, threshold=0.03):
            eattr = G.get_edge_data(*edge)
            comparison = eattr.get('comparison', 0)
            w1 = eattr.get('weight1', 0)
            w2 = eattr.get('weight2', 0)
            label = "{:.2f} ({} vs {})".format(
                comparison, w1, w2
            )
            color = 'grey'
            if w1 and w2:
                if comparison > threshold:
                    color = 'blue'
                elif comparison < -threshold:
                    color = 'green'
            return label, color

        nx1 = Graphitty.render_label(nx1,
                                     use_perc_label=False,
                                     weight_label='comparison',
                                     render_func=render_func)

        return nx1
