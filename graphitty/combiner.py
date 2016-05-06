"""
Combine multiple graphs into one

* Using shorten_name as key
* Compare edges using weight1, weight2
"""


class GraphCombiner(object):

    def __init__(self, g1, g2):
        self.G = self.combine_graph(g1, g2)

    def create_graph(self):
        return self.G

    @classmethod
    def combine_graph(cls,
                      g1, g2):
        # 1. get shortname of g1
        nx1, _ = g1.shorten_name()
        nx2, _ = g2.shorten_name()

        nx1.add_nodes_from(nx2)
        # nx1.add_edges_from(nx2)
        edge_data = {}
        g1_edges = nx1.edges()
        for n1, n2 in g1_edges:
            eattr = nx1.get_edge_data(n1, n2)
            nx1[n1][n2]['weight1'] = eattr.get('weight', 0)

        for n1, n2 in nx2.edges():
            eattr = nx2.get_edge_data(n1, n2)
            if (n1, n2) in g1_edges:
                nx1[n1][n2]['weight2'] = eattr.get('weight', 0)
            else:
                nx1.add_edge(n1, n2,
                             weight2=eattr.get('weight', 0))

        return nx1
