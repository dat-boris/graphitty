from collections import Counter

import networkx as nx
import pandas as pd


class Graphitty(object):
    """
    A class that allows parsing a dataframe containing a timeseries data
    into a directed graph.
    """

    def __init__(self, df,
                 id_col,
                 beahivour_col,
                 ts_col,
                 init=True
                 ):
        self.graph_edges = Counter()
        self.df = df
        self.behaviour_col = beahivour_col
        self.id_col = id_col
        self.ts_col = ts_col
        self.G = None
        if init:
            self.build_path()

    def build_path(self):
        """
        Parse dataframe into `graph_edges`
        """
        path_aggregate = pd.DataFrame(
            self.df.groupby(self.id_col).apply(
                self.get_template_path),
            columns=['path']
        )
        return path_aggregate

    def get_template_path(self, group, add_exit=True):
        """
        Internal function for parsing path. Can be overridden to customize
        behaviour for generating path

        :param: add_exit [bool] Add an exit node
        """
        sorted_time = group.sort(self.ts_col)
        seen_templates = {}
        path = ['start']
        for _, row in sorted_time.iterrows():
            try:
                t = row[self.behaviour_col].strip()
            except AttributeError:
                # skip row
                continue
            if t not in seen_templates:
                seen_templates[t] = 1
                path.append(t)
                if len(path) >= 2:
                    self.graph_edges[(path[-2], path[-1])] += 1
        if add_exit:
            path.append('exit')
            self.graph_edges[(path[-2], path[-1])] += 1
        return ','.join(path)

    def create_graph(self,
                     min_edges=10,
                     use_perc_label=True,
                     filter_subgraph=True,
                     skip_backref=True,
                     MAX_COUNT=100):
        """
        Create a networkx

        :return: Network x graph
        """
        G = nx.DiGraph()
        added_edges = {}

        # TODO: better colour map
        # http://stackoverflow.com/questions/14777066/
        #   matplotlib-discrete-colorbar
        color_array = ['red', 'orange', 'yellow', 'grey']
        if use_perc_label:
            color_array.reverse()

        for i, (e, count) in enumerate(
                self.graph_edges.most_common(MAX_COUNT)):
            if count >= min_edges:
                if skip_backref and ((e[1], e[0]) in added_edges):
                    continue

                # print "Added edge: {}".format([e[0],e[1]])
                label = count
                if use_perc_label:
                    # get all in edge
                    in_count = sum([
                        c for (n0, n1), c
                        in self.graph_edges.iteritems()
                        if n1 == e[0]
                    ])
                    if in_count == 0:
                        out_count = sum([
                            c for (n0, n1), c
                            in self.graph_edges.iteritems()
                            if n0 == e[0]
                        ])
                        label = 100. * count / out_count
                    else:
                        label = 100. * count / in_count

                G.add_edge(e[0], e[1],
                           weight=count,
                           # label="{:.1f}%".format(
                           #     label) if use_perc_label else label,
                           label=count,
                           color=color_array[
                               int((float(label) / MAX_COUNT) *
                                   (len(color_array) - 1))]
                           )
                added_edges[(e[1], e[0])] = 1

        if filter_subgraph:
            U = G.to_undirected()
            nodes = nx.shortest_path(U, 'start').keys()
            G = G.subgraph(nodes)

        self.G = G
        return G

    def simplify(self, condense=True):
        """
        Return an edge contract version of the graph for simplification
        """
        assert self.G, "Must run create_graph before"
        G = self.G.copy()

        seen_nodes = set()
        edges_to_include = set()
        for path in nx.all_simple_paths(G, source='start', target='exit'):
            seen_nodes.update(path)
            for i in range(len(path) - 1):
                edges_to_include.add((path[i], path[i + 1]))

        # for e in G.edges():
        #     if (e[0], e[1]) not in edges_to_include:
        #         G.remove_edge(*e)

        for n in G.nodes():
            if n not in seen_nodes:
                G.remove_node(n)

        # for cyc in nx.simple_cycles(G):
        #     # now we try to break each cycle with the edges that is minimal
        #     # TODO: be smart about this
        #     edge_chosen = (cyc[-2], cyc[-1])
        #     G.remove_edge(*edge_chosen)

        # assert len(list(nx.simple_cycles(G))) == 0, "Seen cycle in graph"

        if condense:
            scc = list(nx.strongly_connected_components(G))
            G = nx.condensation(G, scc=scc)

            relabel_mapping = {}
            for node in G.nodes():
                component = scc[node]
                relabel_mapping[node] = ','.join(component)

            G = nx.relabel_nodes(G, relabel_mapping)

        return G
