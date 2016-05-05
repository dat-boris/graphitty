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
                     node_mapping=None,
                     MAX_COUNT=100):
        """
        Create a networkx

        :param: node_mapping dict - a dictionary of {dst : [src]}

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

        # consider node_mapping data
        # build a mapping of the src -> dst node
        mapped_edge_count = Counter()

        if node_mapping:
            src_dst_mapping = {}
            for dst, src_list in node_mapping.iteritems():
                for src in src_list:
                    src_dst_mapping[src] = dst

            for i, (e, count) in enumerate(
                    self.graph_edges.most_common(MAX_COUNT)):

                src_node = src_dst_mapping.get(e[0], e[0])
                dst_node = src_dst_mapping.get(e[1], e[1])

                mapped_edge_count[(src_node, dst_node)] += count
        else:
            mapped_edge_count = self.graph_edges

        for i, (e, count) in enumerate(
                mapped_edge_count.most_common(MAX_COUNT)):

            if count >= min_edges:
                if skip_backref and ((e[1], e[0]) in added_edges):
                    continue

                # print "Added edge: {}".format([e[0],e[1]])
                label = count
                if use_perc_label:
                    # get all in edge
                    in_count = sum([
                        c for (n0, n1), c
                        in mapped_edge_count.iteritems()
                        if n1 == e[0]
                    ])
                    if in_count == 0:
                        out_count = sum([
                            c for (n0, n1), c
                            in mapped_edge_count.iteritems()
                            if n0 == e[0]
                        ])
                        label = 100. * count / out_count
                    else:
                        label = 100. * count / in_count

                try:
                    edge_color = color_array[
                        int((float(label) / MAX_COUNT) *
                            (len(color_array) - 1))]
                except IndexError:
                    edge_color = 'grey'

                G.add_edge(e[0], e[1],
                           weight=count,
                           label="{:.1f}%".format(
                               label) if use_perc_label else label,
                           color=edge_color)
                added_edges[(e[1], e[0])] = 1

        if filter_subgraph:
            U = G.to_undirected()
            nodes = nx.shortest_path(U, 'start').keys()
            G = G.subgraph(nodes)

        self.G = G
        return G

    def simplify(self,
                 condense=True,
                 relabel=True,
                 min_edges=10,
                 use_perc_label=True,
                 filter_subgraph=True,
                 skip_backref=True,
                 MAX_COUNT=100):
        """
        Return an edge contract version of the graph for simplification
        """
        G = self.create_graph(
            min_edges=min_edges,
            use_perc_label=min_edges,
            filter_subgraph=filter_subgraph,
            skip_backref=skip_backref,
            # note that we use empty node_mapping
            node_mapping=None,
            MAX_COUNT=MAX_COUNT)

        scc = list(nx.strongly_connected_components(G))
        G = nx.condensation(G, scc=scc)

        relabel_mapping = {}
        for node in G.nodes():
            node_name = "[{}] {}".format(
                len(scc[node]),
                ','.join(scc[node])
            )
            relabel_mapping[node_name] = scc[node]

        G2 = self.create_graph(
            min_edges=min_edges,
            use_perc_label=min_edges,
            # disable subgraph filtering
            # (since 'start' node might not be there)
            filter_subgraph=False,
            skip_backref=skip_backref,
            node_mapping=relabel_mapping,
            MAX_COUNT=MAX_COUNT)

        return G2
