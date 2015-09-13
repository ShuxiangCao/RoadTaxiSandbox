__author__ = 'coxious'

from simulator import *
from core import *
import math
import strategy

cross_count = G.num_vertices()

random_vertex = lambda :G.vertex(random.randint(0,cross_count))

entities_lock = threading.Lock()

def get_random_station_pos():
    pos = random_vertex()
    while G.vertex_properties['shape'][pos] != 'circle':
        pos = random_vertex()
    return pos

road_status_dict = {}
road_taxi_dict = {}

for edge in G.edges():
    road_status_dict[G.edge_index[edge]] = 0
    road_taxi_dict[G.edge_index[edge]] = []

def get_road_current_speed(road):
    global  current_time
    return strategy.velocity(G.edge_properties['distance'][road],
                road_status_dict[G.edge_index[road]],
                G.edge_properties['type'][road],0
        )

def get_raod_max_speed(road):
    return road_speed_dict[G.edge_properties['type'][road]]

class Taxi(object):
    def __init__(self,position,self_vertex,w):
        self.last_pass_vertex = position

        self.current_road = None
        self.w = w

        self.accuposition = get_cross_position(position)

        self.status   = 'empty'
        self.customer = None
        self.self_vertex = self_vertex
        #print 'init~~~~~',self_vertex
        self.path = ([],[])

    def __update_position_one_sec(self,t):

        pos_target = get_cross_position(self.target)
        accuposition = get_cross_position(self.self_vertex)

        dy = ( pos_target[1] - accuposition[1] )
        dx = ( pos_target[0] - accuposition[0] )
        ds = math.sqrt( dx **2 + dy ** 2)

        if ds == 0:
            return True

        self.speed = get_road_current_speed(self.current_road)/1000  # to km/s

        #print self.speed

        if ds < self.speed * sec_per_cycle:
            update_taxi_position(self.self_vertex,pos_target)
            return True

        x = accuposition[0] + self.speed * sec_per_cycle * dx/ds
        y = accuposition[1] + self.speed * sec_per_cycle * dy/ds

        update_taxi_position(self.self_vertex,(x,y))

        return False

    def run_time_elapse(self,time):
       try:
            if self.current_road == None:
                if self.status == 'empty':
                   self.current_road = get_random_road_from_position(self.last_pass_vertex)
                else:
                    self.current_road = self.path[1][0]
                    self.path[1].remove(self.current_road)

                entities_lock.acquire()
                road_status_dict[G.edge_index[self.current_road]] += 1
                road_taxi_dict[G.edge_index[self.current_road]] .append(self)
                entities_lock.release()
       except:
           pass

       self.target = get_road_target(self.last_pass_vertex,self.current_road)

       if self.__update_position_one_sec(time):
           self.last_pass_vertex = get_road_target(self.last_pass_vertex,self.current_road)
           entities_lock.acquire()
           road_status_dict[G.edge_index[self.current_road]] -= 1
           road_taxi_dict[G.edge_index[self.current_road]] .remove(self)
           entities_lock.release()
           self.current_road = None

           if len(self.path[1]) == 0:
                if self.status == 'picking up':
                    self.path = self.customer.path
                    self.customer.set_on_trip()
                    self.status = 'on trip'
                    change_taxi_color(self.self_vertex,False)
                elif self.status == 'on trip':
                    self.status = 'empty'
                    change_taxi_color(self.self_vertex,True)
                    self.customer.set_finish()

    def inform_new_customer(self,customer):
        if self.status == 'empty' and strategy.take_or_not(self,customer):

            self.customer = customer
            self.status = 'picking up'

            customer.set_waiting(self)

            self.path = gt.shortest_path(G_no_moving,self.last_pass_vertex,
               customer.start_position,G.edge_properties['distance'])

            vertex,edge = self.path

            if self.current_road not in edge:
               # Turn around
                self.last_pass_vertex = get_road_target(self.last_pass_vertex,self.current_road)
            return True
        return False

class Customer(object):
    def __init__(self,position,self_vertex):
        self.status = "Calling"
        self.target = get_random_station_pos()
        self.start_position = position
        self.path = \
            gt.shortest_path(G_no_moving,self.start_position,self.target ,G.edge_properties['distance'])
        self.taxi = None
        self.self_vertex = self_vertex

        dispatcher = CustomerDispather(self)
        gt.bfs_search(G,self.start_position,dispatcher)

    def set_waiting(self,taxi):
        self.taxi = taxi
        self.status = "Waiting"

    def set_on_trip(self):
        self.status = "OnTrip"
        add_inactive_vertex(self.self_vertex)

    def set_finish(self):
        self.status = "Finish"
        print "I'm finished"

    def run_time_elapse(self):
        pass

class CustomerDispather(gt.BFSVisitor):
    def __init__(self,customer):
        self.customer = customer

    def examine_edge(self, e):
        taxi_on_road = road_taxi_dict[G.edge_index[e]]

        entities_lock.acquire()
        for taxi in taxi_on_road:
            if taxi.inform_new_customer(self.customer):
                entities_lock.release()
                raise gt.StopSearch

        entities_lock.release()
