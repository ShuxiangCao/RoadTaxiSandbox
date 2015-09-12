__author__ = 'coxious'

from simulator import *
from core import *
import math

cross_count = G.num_vertices()

random_vertex = lambda :G.vertex(random.randint(0,cross_count))

class Taxi(object):
    def __init__(self,position,self_vertex):
        self.last_pass_vertex = position

        self.current_road = None

        self.accuposition = get_cross_position(position)

        self.speed    = 1 /3.6 /5000 #km /h
        self.status   = 'empty'
        self.customer = None
        self.self_vertex = self_vertex

    def __update_position_one_sec(self):
        pos_target = get_cross_position(self.target)
        accuposition = get_cross_position(self.self_vertex)

        distance = math.sqrt(( pos_target[1] - accuposition[1] )**2 +
                             ( pos_target[0] - accuposition[0] ) ** 2)

        if distance < self.speed:
            self.accuposition = pos_target
            return True

        if accuposition[0] == pos_target[0]:

            theta = 0.5 * math.pi * (( pos_target[1] - accuposition[1] ) / abs(( pos_target[1] - accuposition[1] )))
        else:
            tan =  ( pos_target[1] - accuposition[1] ) / ( pos_target[0] - accuposition[0] )
            theta = math.atan(tan)

        x = accuposition[0] + self.speed * math.cos(theta)
        y = accuposition[1] + self.speed * math.sin(theta)

        #print accuposition,(x,y)
        update_taxi_position(self.self_vertex,(x,y))
        return False

    def run_time_elapse(self,time):
        if self.status == 'empty':
            if self.current_road== None:
                self.current_road = get_random_road_from_position(self.last_pass_vertex)
            self.target = get_road_target(self.last_pass_vertex,self.current_road)

            if self.__update_position_one_sec():
                self.last_pass_vertex = get_road_target(self.last_pass_vertex,self.current_road)
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

