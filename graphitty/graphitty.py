import math
import re
from collections import Counter, defaultdict

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
                 init=True,
                 node_mapping=None,
                 skip_backref=True,
                 max_edges=200,
                 min_edges=0
                 ):
        self.df = df
        self.behaviour_col = beahivour_col
        self.id_col = id_col
        self.ts_col = ts_col
        self.G = None
        self.add_edge_callback = None

        if init:
            self.build_path(node_mapping=node_mapping,
                            skip_backref=skip_backref,
                            min_edges=min_edges,
                            max_edges=max_edges)
            assert len(self.G.nodes()) > 0

    def build_path(self,
                   node_mapping=None,
                   skip_backref=True,
                   max_edges=200,
                   min_edges=0):
        """
        Parse dataframe into Network X edges
        """
        edge_count = Counter()

        if node_mapping:
            src_dst_mapping = {}
            for dst, src_list in node_mapping.iteritems():
                for src in src_list:
                    src_dst_mapping[src] = dst

        def add_edge_callback(n1, n2):
            if node_mapping:
                n1 = src_dst_mapping.get(n1, n1)
                n2 = src_dst_mapping.get(n2, n2)
            edge_count[(n1, n2)] += 1

        self.add_edge_callback = add_edge_callback
        path_aggregate = pd.DataFrame(
            self.df.groupby(self.id_col).apply(
                self.get_template_path),
            columns=['path']
        )

        assert len([n for n in edge_count.keys() if 'start' in n[0]]) > 0

        self.G = self.__create_graph_from_edges(
            edge_count, skip_backref=skip_backref,
            min_edges=min_edges,
            max_edges=max_edges
        )

        # now given the edges, create the nxgraph
        return path_aggregate

    def __create_graph_from_edges(self, edge_count,
                                  min_edges=0,
                                  skip_backref=True,
                                  max_edges=200):
        G = nx.DiGraph()
        added_edges = {}

        for i, (e, count) in enumerate(edge_count.most_common(max_edges)):
            if (min_edges is not None) and (count < min_edges):
                continue
            if skip_backref and ((e[1], e[0]) in added_edges):
                continue
            # print "Added edge: {}".format([e[0],e[1]])
            G.add_edge(e[0], e[1], weight=count)
            added_edges[(e[0], e[1])] = 1
        return G

    def get_template_path(self, group,
                          add_exit=True,
                          add_edge_callback=None):
        """
        Internal function for parsing path. Can be overridden to customize
        behaviour for generating path

        :param: add_exit [bool] Add an exit node
        """
        if not add_edge_callback:
            add_edge_callback = self.add_edge_callback
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
                    if add_edge_callback:
                        add_edge_callback(path[-2], path[-1])
        if add_exit:
            path.append('exit')
            if add_edge_callback:
                add_edge_callback(path[-2], path[-1])
        return path

    def render_graph(self,
                     use_perc_label=True,
                     filter_subgraph=True):
        """
        Create a networkx

        :param: node_mapping dict - a dictionary of {dst : [src]}

        :return: Network x graph
        """
        G = self.G
        G = self.render_label(G, use_perc_label=use_perc_label)
        if filter_subgraph:
            G = self.filter_subgraph(G)
        return G

    @classmethod
    def render_label(cls, G,
                     use_perc_label=True,
                     weight_label='weight',
                     render_func=None):
        """
        Apply label rendering to graph
        """

        graph_edges = G.edges(data=True)
        mapped_edge_count = {
            (n0, n1): d.get(weight_label)
            for n0, n1, d in graph_edges
        }

        if render_func is None:
            # TODO: better colour map
            # http://stackoverflow.com/questions/14777066/
            #   matplotlib-discrete-colorbar
            color_array = ['red', 'orange', 'yellow', 'grey']
            if use_perc_label:
                color_array.reverse()

            max_weight = 100 if use_perc_label else max(
                mapped_edge_count.values())

        def default_renderer(G, e, count):
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
            else:
                label = count

            try:
                edge_color = color_array[
                    int((float(label) / max_weight) *
                        (len(color_array) - 1))]
            except IndexError:
                edge_color = 'grey'
            label = "{:.1f}%".format(label) if use_perc_label else label
            return label, edge_color

        if render_func is None:
            render_func = default_renderer

        for e, count in mapped_edge_count.iteritems():
            label, edge_color = render_func(G, e, count)
            G[e[0]][e[1]].update({
                'label': label,
                'color': edge_color
            })
        return G

    def get_node(self, G, name):
        for n in G.nodes():
            if name in str(n):
                return n
        raise IndexError("No node {} found! nodes = {}".format(
            name, G.nodes()))

    def filter_subgraph(self, G, max_path=10):
        seen_nodes = set()
        for path in self.get_path_in_weight_order(G)[:max_path]:
            seen_nodes.update(path)
        for n in G.nodes():
            if n not in seen_nodes:
                G.remove_node(n)
        return G

    def get_path_in_weight_order(self, G):
        paths = nx.all_simple_paths(G,
                                    source=self.get_node(G, 'start'),
                                    target=self.get_node(G, 'exit')
                                    )
        return sorted(paths,
                      key=lambda p: G[p[0]][p[1]].get('weight'),
                      reverse=True)

    def simplify(self):
        """
        Return an edge contract version of the graph for simplification

        NOTE: return new graph
        """
        mapping = self.get_simplify_mapping()
        g = Graphitty(
            self.df,
            id_col=self.id_col,
            beahivour_col=self.behaviour_col,
            ts_col=self.ts_col,
            node_mapping=mapping)

        assert len(g.G.nodes()) > 0
        return g

    def get_simplify_mapping(self, shorten=True):
        assert self.G
        G = self.G

        scc = list(nx.strongly_connected_components(G))
        G = nx.condensation(G, scc=scc)

        relabel_mapping = {}
        for node in G.nodes():
            node_name = "[{}] {}".format(
                len(scc[node]),
                ','.join(scc[node])
            )
            relabel_mapping[node_name] = scc[node]

        if shorten:
            shorten_mapping = self.shorten_name(
                node_list=relabel_mapping.keys()
            )
            relabel_mapping = {
                shorten_mapping[old_name]: orig_nodes
                for old_name, orig_nodes in relabel_mapping.iteritems()
            }

        return relabel_mapping

    def shorten_name(self,
                     node_list=None,
                     top_terms=3,
                     black_list_term={'html'}):
        """
        Shorten node name of graph

        :return: label_mapping (dict of orig_name -> new_name)
        """
        relabel_mapping = {}
        # use inverse doc frequency mapping

        if node_list is None:
            node_list = G.nodes()
            G = self.G
        else:
            G = None

        def tokenizer(s):
            return [
                t for t in re.split(r'[^\w\d-]+', s)
                if len(t) >= 3 and t not in black_list_term
            ]
        token_docs = [tokenizer(n) for n in node_list]
        tf_idf_counts = tf_idf(token_docs)
        for i, n in enumerate(node_list):
            tf_counter = tf_idf_counts[i]
            name = ' + '.join(
                [
                    t[0] for t in tf_counter.most_common(top_terms)
                ])
            relabel_mapping[n] = name
        if G is not None:
            self.G = nx.relabel_nodes(G, relabel_mapping)

        return relabel_mapping


def tf_idf(docs, max_doc_freq=None):
    """
    Calculate tf, idf for each item

    :param: max_doc_freq - only allow terms which are unique
    """
    number_of_docs = len(docs)
    if not max_doc_freq:
        max_doc_freq = number_of_docs

    doc_freq = Counter()
    doc_term_freq = []
    for i, doc in enumerate(docs):
        term_freq = Counter()
        for term in doc:
            term_freq[term] += 1
        for term in list(set(doc)):
            doc_freq[term] += 1
        doc_term_freq.append(term_freq)

    all_df_idf = []
    for term_freq in doc_term_freq:
        df_idf = Counter()
        for term, tf_count in term_freq.most_common(10):
            if doc_freq[term] > max_doc_freq:
                continue
            df_idf[term] = tf_count * math.log(
                (1. * number_of_docs / doc_freq[term]))
        assert len(df_idf) > 0, \
            "Cannot find unique name for doc: {}".format(term_freq)
        all_df_idf.append(df_idf)

    return all_df_idf
