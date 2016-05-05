
# Graphitty

A Python library that convert time series to direction Graph to discover the story within data.


![Example graph](apollo.png)


[![Circle CI](https://circleci.com/gh/sketchytechky/graphitty.svg?style=svg&circle-token=<cirlce-ci-token>)](https://circleci.com/gh/sketchytechky/graphitty)

# Installing

To install this package, runs:

    pip install https://github.com/sketchytechky/graphitty.git

Remember to add the following line to `requirements.txt`

    git+https://github.com/sketchytechky/graphitty.git


-----------


# How to use

```
import pandas as pd

df = pd.DataFrame(
        [...],
        columns=['timestamp','action'])

gf = GraphFrame(df, ts='timestamp', action='action')

nx_graph = gf.gengraph()

# create the beautiful directional graph
draw(nx_graph)
```

# Running Tests

Run test with

    py.test --pep8

To run test in watch mode

    py.test.watch -- --pep8
    # same with: ptw -- --pep8


-----------


# Related research


* Information Foraging Theory:Adaptive Interaction with Information - http://www.peterpirolli.com/Professional/About_Me_files/IFT%20Ch%201.pdf


* Jakob Nielson example on how to apply information foraging theory to understand visitor's behaviour
  - http://www.useit.com/alertbox/scrolling-attention.html
  - https://www.nngroup.com/articles/information-scent/

