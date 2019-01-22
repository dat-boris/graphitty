import pandas as pd


class Funnel(object):
    """
    Simulate the funnel of each step across the graph
    """

    def __init__(self, path, df, graph):
        self.funnel_path = path
        self.graph = graph

        self.steps = self.identify_user_steps(path, graph)
        # self.mark_df_funnel_steps()

    def is_common_path(self, user_path, funnel_path=None):
        """ Identify the maximum path that user have in common
        e.g. funnel = [1,2,3,4,5], user = [1,a,2,b,3] -> [1,2,3]
        """
        if funnel_path is None:
            funnel_path = self.funnel_path
        common_path = []
        user_idx = 0
        for s in funnel_path:
            while user_idx < len(user_path):
                if s == user_path[user_idx]:
                    common_path.append(s)
                    user_idx += 1
                    break
                user_idx += 1
        return common_path

    def identify_user_steps(self, funnel_path, graph):
        steps = [
            {'name': s, 'user': []}
            for s in funnel_path
        ]
        for user_id, path in graph.path_aggregate_df.iterrows():
            common_path = self.is_common_path(path.path)
            for i, p in enumerate(common_path):
                steps[i]['user'].append(user_id)
        return steps

    def describe_steps(self):
        self.funnel_df = pd.DataFrame({
            'name': [s['name'] for s in self.steps],
            'user_count': [len(s['user']) for s in self.steps]
        }).set_index('name')
        self.funnel_df['drop_off'] = 100. * (
            1 - self.funnel_df.user_count / self.funnel_df.user_count.shift(1)
        )
        return self.funnel_df
