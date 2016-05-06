from __future__ import division

import pandas as pd


class Comparator(object):

    @staticmethod
    def compare_value(v1, v2,
                      total1,
                      total2):
        return v1 / total1 - v2 / total2

    @staticmethod
    def compare_list(df1, df2,
                     total1=None,
                     total2=None,
                     count1='count',
                     count2='count',
                     threshold=0.20,
                     verbose=False):
        if total1 is None:
            total1 = len(df1)
        if total2 is None:
            total2 = len(df2)

        # 1. compare the total perc
        rate1 = pd.DataFrame(df1[count1] / total1)
        rate2 = pd.DataFrame(df2[count2] / total2)

        # 2. merge the two based on index
        joined = rate1.join(
            rate2,
            lsuffix='l',
            rsuffix='r',
            how='outer',
        ).fillna(0)
        assert len(joined) > 0
        joined['compare'] = joined[count1 + 'l'] - joined[count2 + 'r']

        seen_df = joined[
            (joined.compare > threshold) | (joined.compare < -threshold)]

        if verbose:
            print joined
        return joined
