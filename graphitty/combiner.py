"""
Combine multiple graphs into one

* Using shorten_name as key
* Compare edges using weight1, weight2
"""

from .graphitty import Graphitty
from .comparator import Comparator


class GraphCombiner(Graphitty):

    def __init__(self, g1, g2, simplify=False):
        self.total1 = None
        self.total2 = None
        self.G = self.combine_graph(g1, g2, simplify=simplify)

    def create_graph(self):
        return self.G

    def combine_graph(self,
                      g1, g2,
                      simplify=False):
        # 1. get shortname of g1
        g1.shorten_name()
        g2.shorten_name()
        return self.combine_nx_graph(g1.G, g2.G)

    def combine_nx_graph(self, nx1, nx2):
        nx1.add_nodes_from(nx2)
        # nx1.add_edges_from(nx2)
        edge_data = {}
        g1_edges = nx1.edges()
        self.total1 = 0
        self.total2 = 0
        for n1, n2 in g1_edges:
            weight = nx1.get_edge_data(n1, n2).get('weight', 0)
            nx1[n1][n2]['weight1'] = weight
            self.total1 += weight

        for n1, n2 in nx2.edges():
            weight = nx2.get_edge_data(n1, n2).get('weight', 0)
            if (n1, n2) in g1_edges:
                nx1[n1][n2]['weight2'] = weight
            else:
                nx1.add_edge(n1, n2,
                             weight2=weight)
            self.total2 += weight

        return nx1

    def simplify(self):
        super(GraphCombiner, self).simplify(
            combine_fields=['weight1', 'weight2'])

    def do_compare(self):
        # now execute comparison
        G = self.G
        for n1, n2 in G.edges():
            eattr = G.get_edge_data(n1, n2)
            G[n1][n2]['comparison'] = Comparator.compare_value(
                eattr.get('weight1', 0),
                eattr.get('weight2', 0),
                total1=self.total1,
                total2=self.total2
            )

    def render_graph(self, filter_subgraph=True):

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

        G = self.render_label(self.G,
                              use_perc_label=False,
                              weight_label='comparison',
                              render_func=render_func)

        if filter_subgraph:
            G = self.filter_subgraph(G)
        return G
