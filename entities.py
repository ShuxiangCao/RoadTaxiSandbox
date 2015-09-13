__author__ = 'coxious'

from simulator import *
from core import *
import math
import strategy
import numpy as np

cross_count = G.num_vertices()

random_vertex = lambda :G.vertex(random.randint(0,cross_count))

entities_lock = threading.Lock()

active_customer_list = []
taxies_list = []

current_time = 0

total_request = 0
no_response_request = 0
finished_count = 0
on_trip_count = 0

dict_overview = {
    'taxi_free_rate' : 0.,
    'waiting_customers' : 0.,
    'average_decline_rate' : 0.,
    'highest_decline_rate' : 0.,
    'lowest_decline_rate' : 0.,
    'total_call':0.,
    'no_response_call':0.,
    'no_response_rate' : 0.,
    'averange_speed':0.,
    'on_trip_count':0.,
    'finished_count':0.
}

data_point_customer = pd.DataFrame()
data_road_density   = pd.DataFrame()
data_overview = pd.DataFrame(columns= dict_overview.keys())

road_status_dict = {}
road_taxi_dict = {}
point_customer_dict = {}

for edge in G.edges():
    road_status_dict[G.edge_index[edge]] = 0
    road_taxi_dict[G.edge_index[edge]] = []

for vertex in G.vertices():
    point_customer_dict[G.vertex_index[vertex]] = []

def get_random_station_pos():
    pos = random_vertex()
    while G.vertex_properties['shape'][pos] != 'circle':
        pos = random_vertex()
    return pos

def statistics():

    def get_free_rate():
        free_taxi_count = 0
        for taxi in taxies_list:
            if taxi.status == 'empty':
                free_taxi_count += 1.
        return free_taxi_count,free_taxi_count / len(taxies_list)

    def get_waiting_customers():
        waiting_customers_count = 0
        for customer in active_customer_list:
            if customer.status == 'Waiting':
                waiting_customers_count += 1
        return waiting_customers_count,waiting_customers_count/len(active_customer_list)

    dict_overview['taxi_free_rate'] = get_free_rate()
    dict_overview['waiting_customers'] = get_waiting_customers()
    dict_overview['average_decline_rate'] = np.average([1. * x.declined_times / x.requested_times for x in taxies_list])
    dict_overview['highest_decline_rate'] = np.max([1. * x.declined_times / x.requested_times for x in taxies_list])
    dict_overview['lowest_decline_rate'] = np.min([1. * x.declined_times / x.requested_times for x in taxies_list])
    dict_overview['total_call'] = total_request
    dict_overview['no_response_call'] = no_response_request
    dict_overview['no_response_rate'] = no_response_request / total_request

    dict_overview['averange_speed'] = np.average([get_road_current_speed(x.current_road) for x in taxies_list ]) * 3.6

    dict_overview['on_trip_count'] = on_trip_count
    dict_overview['finished_count'] = finished_count

    global  data_overview
    serie = pd.Series(dict_overview)
    data_overview = data_overview.append(serie,ignore_index=True)

    print serie

def save_data():
    data_overview.to_csv(base_path + 'overview.csv')

def get_road_current_speed(road):
    if not road:
        return 0
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

        self.requested_times= 1
        self.declined_times = 0
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
       if not self.current_road:
           if self.status == 'empty':
              self.current_road = get_random_road_from_position(self.last_pass_vertex)
           else:
               self.current_road = self.path[1][0]
               self.path[1].remove(self.current_road)

           entities_lock.acquire()
           road_status_dict[G.edge_index[self.current_road]] += 1
           road_taxi_dict[G.edge_index[self.current_road]] .append(self)
           entities_lock.release()

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

        self.requested_times += 1

        if self.status != 'empty':
            self.declined_times += 1

        return False

class Customer(object):
    def __init__(self,position,self_vertex):
        self.status = "Calling"
        self.start_position = position
        point_customer_dict[G.vertex_index[self.start_position]].append(self)

        while(True):

            self.target = get_random_station_pos()

            #customer_trip_distance =\
            #    gt.shortest_distance(G_no_moving,self.start_position,self.target ,G.edge_properties['distance'])

            pos_source = G.vertex_properties['position'][self.start_position]
            pos_target = G.vertex_properties['position'][self.target]

            distance = math.sqrt((pos_source[0] - pos_target[0])**2 + (pos_source[1] - pos_target[1])**2)

            if distance < max_customer_distance and self.target != self.start_position:
                break

        self.path = \
            gt.shortest_path(G_no_moving,self.start_position,self.target ,G.edge_properties['distance'])

        self.taxi = None
        self.self_vertex = self_vertex

        self.make_call()
        self.start_waiting = 0
        self.end_waiting = 0

    def make_call(self):
        global  total_request
        global  no_response_request
        total_request += 1
        dispatcher = CustomerDispather(self)
        gt.bfs_search(G,self.start_position,dispatcher)

        if self.status == 'Calling':
            no_response_request += 1
            add_inactive_vertex(self.self_vertex)
            point_customer_dict[G.vertex_index[self.start_position]].remove(self)

    def set_waiting(self,taxi):
        self.taxi = taxi
        self.status = "Waiting"
        self.start_waiting = 0

    def set_on_trip(self):
        self.status = "OnTrip"

        global  on_trip_count
        on_trip_count += 1

        add_inactive_vertex(self.self_vertex)
        point_customer_dict[G.vertex_index[self.start_position]].remove(self)

    def set_finish(self):
        global  finished_count
        global  on_trip_count
        finished_count += 1
        on_trip_count -= 1
        self.status = "Finish"
        self.end_waiting = 0

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
