"""
This is responsible for doing comparison for a simple list
"""

import pandas as pd
from graphitty.comparator import Comparator


def test_compare_list():
    t1 = 69360
    l1 = pd.DataFrame({'/history/apollo/apollo-13/apollo-13.html': 13756,
                       '/history/apollo/apollo.html': 14456,
                       '/history/history.html': 11802,
                       '/ksc.html': 40072,
                       '/shuttle/countdown/countdown.html': 8558,
                       '/shuttle/countdown/liftoff.html': 21981,
                       '/shuttle/missions/missions.html': 24834,
                       '/shuttle/missions/sts-70/mission-sts-70.html': 16103,
                       '/shuttle/missions/sts-71/images/images.html': 15881,
                       '/shuttle/missions/sts-71/mission-sts-71.html': 16698}
                      .items(),
                      columns=['url', 'count']
                      ).set_index('url')

    t2 = 64455
    l2 = pd.DataFrame({'/history/apollo/apollo-13/apollo-13.html': 7160,
                       '/history/apollo/apollo.html': 8973,
                       '/history/history.html': 10111,
                       '/ksc.html': 43619,
                       '/shuttle/countdown/liftoff.html': 7858,
                       '/shuttle/missions/missions.html': 22429,
                       '/shuttle/missions/sts-69/images/images.html': 5261,
                       '/shuttle/missions/sts-69/mission-sts-69.html': 24592,
                       '/shuttle/technology/sts-newsref/stsref-toc.html': 6506,
                       '/software/winvn/winvn.html': 10343}.items(),
                      columns=['url', 'count']
                      ).set_index('url')

    comparator_list = Comparator.compare_list(
        l1, l2,
        total1=t1,
        total2=t2
    )

    assert len(comparator_list) > 2
