__author__ = 'coxious'

from config import *
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import graph_tool.all as gt
import math
import random

G =  gt.load_graph(base_path + graph_tool_file)

class Taxi(object):

    def __init__(self,position,road):
        self.position = None
        self.current_road = None
        self.speed    = None
        self.status   = None
        self.customer = None
        pass

class Customer(object):
    def __init__(self):
        self.status = "Calling"
        self.target = None
        self.start_position = None
        pass

#gt.graph_draw(G,G.vertex_properties['position'],output=base_path + 'test.pdf')

print G.num_vertices()
print G.num_edges()


