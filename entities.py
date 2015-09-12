__author__ = 'coxious'

from simulator import *
from core import *
import math
import strategy

cross_count = G.num_vertices()

random_vertex = lambda :G.vertex(random.randint(0,cross_count))

road_status_dict = {}

for edge in G.edges():
    road_status_dict[G.edge_index[edge]] = 0

class Taxi(object):
    def __init__(self,position,self_vertex):
        self.last_pass_vertex = position

        self.current_road = None

        self.accuposition = get_cross_position(position)


        self.status   = 'empty'
        self.customer = None
        self.self_vertex = self_vertex

    def __update_position_one_sec(self):

        pos_target = get_cross_position(self.target)
        accuposition = get_cross_position(self.self_vertex)

        dy = ( pos_target[1] - accuposition[1] )
        dx = ( pos_target[0] - accuposition[0] )
        ds = math.sqrt( dx **2 + dy ** 2)

        if ds == 0:
            return True

        self.speed = strategy.velocity(G.edge_properties['distance'][self.current_road],
                road_status_dict[G.edge_index[self.current_road]],
                G.edge_properties['type'][self.current_road]
        )/1000  # to km/s

        #print self.speed

        if ds < self.speed * sec_per_cycle:
            self.accuposition = pos_target
            return True

        x = accuposition[0] + self.speed * sec_per_cycle * dx/ds
        y = accuposition[1] + self.speed * sec_per_cycle * dy/ds

        update_taxi_position(self.self_vertex,(x,y))

        return False

    def run_time_elapse(self,time):
        if self.status == 'empty':
            try:
                if self.current_road == None:
                    self.current_road = get_random_road_from_position(self.last_pass_vertex)
                    road_status_dict[G.edge_index[self.current_road]] += 1
            except:
                pass

            self.target = get_road_target(self.last_pass_vertex,self.current_road)

            if self.__update_position_one_sec():
                self.last_pass_vertex = get_road_target(self.last_pass_vertex,self.current_road)
                road_status_dict[G.edge_index[self.current_road]] -= 1
                self.current_road = None
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

