import abilities
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput

with PyCallGraph(output=GraphvizOutput()):
    abilities.TestCounters().test_dmg_graphs(rotation_lst=abilities.rot3, item_lst=abilities.itemLst2)