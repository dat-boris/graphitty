import random
import pandas as pd
import seaborn as sns
from collections import defaultdict


class Funnel(object):
    """
    Simulate the funnel of each step across the graph
    """

    def __init__(self, path, graph):
        self.funnel_path = path
        self.graph = graph
        self.user_max_steps = {}

        # tranfer parameters from graph
        self.df = graph.df
        self.id_col = graph.id_col
        self.behaviour_col = graph.behaviour_col
        self.ts_col = graph.ts_col

        self.steps = self.identify_user_steps(path, graph)
        self.annotated_df = None

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
            self.user_max_steps[user_id] = len(common_path)
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

    def remove_user(self, user_id):
        if user_id not in self.user_max_steps:
            raise KeyError("User {} not in funnel".format(user_id))
        max_steps = self.user_max_steps[user_id]
        del self.user_max_steps[user_id]
        for s in self.steps[:max_steps]:
            s['user'].remove(user_id)

    def filter_df_by_users(self, df=None, id_col=None, sample=None):
        if df is None:
            df = self.df
        if id_col is None:
            id_col = self.id_col
        user_in_funnel = self.user_max_steps.keys()
        if sample:
            user_in_funnel = random.sample(user_in_funnel, k=sample)
        return df[df[id_col].isin(user_in_funnel)]

    @property
    def funnel_path_in_df(self):
        # These are nodes which is added manually
        ignore_nodes = {'start', 'end'}
        funnel_path = [
            p for p in self.funnel_path if p not in ignore_nodes
        ]
        return funnel_path

    def __label_group(self, group, include_intermediate=False):
        """
        Internal function for parsing path.
        Identify steps that are in those steps and then return those.

        Used in pandas.apply
        Adding two columns:
        * last_step (yes / no)
        * step_count
        """
        funnel_path = self.funnel_path_in_df

        path_idx = 0
        sorted_time = group.sort_values(self.ts_col)
        wanted_steps = []
        for _, row in sorted_time.iterrows():
            # Identify what step the user is at
            path_name = funnel_path[path_idx]
            current_name = row[self.behaviour_col]
            if path_name == current_name:
                path_idx += 1
                # check if user is at last step:
                user_id = row[self.id_col]
                max_step = self.user_max_steps[user_id]
                row['step_count'] = path_idx
                wanted_steps.append(row)
            else:
                if include_intermediate:
                    row['step_count'] = path_idx
                    wanted_steps.append(row)

        if not wanted_steps:
            return None
        return_df = pd.DataFrame(wanted_steps)
        return_df['is_last_step'] = (return_df['step_count'] == path_idx)
        return return_df

    def extract_key_steps_from_df(self, df=None, id_col=None, sample=None):
        """ Given a trail dataframe, extract the key steps
        """
        if df is None:
            df = self.df
        if id_col is None:
            id_col = self.id_col

        filter_df = self.filter_df_by_users(df, sample=sample)

        annotated_df = pd.DataFrame(
            filter_df.groupby(id_col).apply(
                self.__label_group
            )
        ).reset_index(drop=True)
        self.annotated_df = annotated_df
        return annotated_df

    def visualize_dropoff(self, compare_col='sufficiently_usable'):
        annotated_df = self.annotated_df
        funnel_path = self.funnel_path_in_df
        # it doesnt make sense for last step
        for i, step_name in enumerate(funnel_path[:-1]):
            step_df = annotated_df[annotated_df.step_count == i+1]
            sns.jointplot(
                step_df['is_last_step'],
                step_df[compare_col],
                kind='reg'
            ).fig.suptitle(
                'Step {}: comparing {} to dropoff ratio'.format(
                    step_name, compare_col
                ))


class FunnelCombination(object):
    """ This class consider multiple funnel, and remove user who have progressed
    further in other funnel.

    For example:
        Funnel 1: [1, 3, 5]
        Funnel 2: [1, 2, 4]
        User A: [1, 3]

    Then in above case User A will only be considered in Funnel 1.
    """

    def __init__(self, funnels):
        self.funnels = funnels
        user_max_steps = defaultdict(int)

        # identify max steps from user
        for f in funnels:
            for user, max_steps in f.user_max_steps.items():
                if user_max_steps[user] < max_steps:
                    user_max_steps[user] = max_steps

        # remove user that is not suitable
        for user, combine_max_steps in user_max_steps.items():
            for f in funnels:
                max_steps = f.user_max_steps[user]
                if combine_max_steps > max_steps:
                    f.remove_user(user)
        self.user_max_steps = user_max_steps

    @property
    def user_ids(self):
        return set(self.user_max_steps.keys())
