__author__ = 'coxious'

from config import *
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import graph_tool.all as gt
import math
import random

G =  gt.load_graph(base_path + graph_tool_file)

random_vertex = lambda :G.vertex(random.randint(0,G.num_vertices()))

finished_customer = []
living_customer = []
taxies = []

def to_human_time(time):
    hour = int(time / 3600)
    minute = int((time - 3600 * hour)/60)
    second = time - 3600 * hour - 60 * min
    return hour,minute,second

class Taxi(object):
    def __init__(self,position,road):
        self.position = random_vertex()
        self.accuposition = None
        self.next_position = None
        self.speed    = None
        self.status   = None
        self.customer = None
        self.self_vertex = None

    def run_time_elapse(self):
        pass

class Customer(object):
    def __init__(self):
        self.status = "Calling"
        self.target = random_vertex()
        self.start_position = random_vertex()
        self.vertex,self.edge = \
            gt.shortest_path(G,self.start_position,self.target ,G.edge_properties['distance'])
        self.taxi = None
        self.self_vertex = None

    def set_waiting(self,taxi):
        self.taxi = taxi
        self.status = "Waiting"

    def set_on_trip(self):
        self.status = "OnTrip"

    def set_finish(self):
        self.status = "Finish"

    def run_time_elapse(self):
        pass

def update_graph():
    pass

def run_time_elapse(time):
    pass

def run_strategy():
    pass

for time in xrange(24 * 3600):
    run_strategy()
    update_graph()
    run_time_elapse(time)
    hour,minute,sec = to_human_time(time)
    print "Current Hour %d\n"%hour
