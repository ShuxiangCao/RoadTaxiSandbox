__author__ = 'coxious'

from simulator import *
from core import *
from core import *

class Taxi(object):
    def __init__(self,position,self_vertex):
        self.last_pass_vertex = position
        self.current_road = None
        self.accuposition = get_cross_position(position)
        self.speed    = None
        self.status   = 'empty'
        self.customer = None
        self.self_vertex = self_vertex

    def run_time_elapse(self):
        if self.status == 'empty':
            if self.current_road== None:

                pass
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

