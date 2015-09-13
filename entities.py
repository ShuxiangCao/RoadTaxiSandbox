__author__ = 'coxious'

from simulator import *
from core import *
import math
import strategy
import numpy as np
import time

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
    'finished_count':0.,
    'average_waiting_time':0.
}

data_frames = {}

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

    def update_taxies():
        for taxi in taxies_list:
            id = G.vertex_index[taxi.self_vertex]
            data_frames['taxi%d'%id] = data_frames['taxi%d'%id].\
                append(pd.Series(taxi.get_dynamic_attributes()),ignore_index = True)

    def update_customers():
        for customer in active_customer_list:
            id = G.vertex_index[customer.self_vertex]
            data_frames['customer%d'%id] = data_frames['customer%d'%id].\
                append(pd.Series(customer.get_dynamic_attributes()),ignore_index = True)

    def get_free_rate():
        free_taxi_count = 0
        for taxi in taxies_list:
            if taxi.status == 'empty':
                free_taxi_count += 1.
        return free_taxi_count,free_taxi_count / len(taxies_list)

    def get_average_waiting_time():
        waiting_time_sum = 0
        trip_customers_count = 1
        for customer in active_customer_list:
            if customer.status == 'OnTrip':
                trip_customers_count += 1
                waiting_time_sum += (customer.end_waiting - customer.start_waiting)

        return waiting_time_sum/trip_customers_count

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

    dict_overview['average_waiting_time'] = get_average_waiting_time()

    #time_update = time.time()
    #update_customers()
    #update_taxies()
    #print "update all data cost %f\n",time.time()-time_update

    global  data_overview
    serie = pd.Series(dict_overview)
    data_overview = data_overview.append(serie,ignore_index=True)

    print serie

def save_data():

    data_overview.to_csv(frame_path + 'overview.csv')
    #for key,val in data_frames.iteritems():
    #    val.to_csv(frame_path + key)
    data_road_density.to_csv(frame_path + 'road_density.csv')

    taxi_static = None
    for taxi in taxies_list:
        data = taxi.get_static_attributes()
        if type(taxi_static) == type(None):
            taxi_static = pd.DataFrame(columns=data.keys())
        taxi_static.append(pd.Series(data),ignore_index = True)

    customer_static = None
    for customer in active_customer_list:
        data = customer.get_static_attributes()
        if type(customer_static) == type(None):
            customer_static = pd.DataFrame(columns=data.keys())
        customer_static.append(pd.Series(data),ignore_index = True)

    taxi_static.to_csv(frame_path + 'taxi_static.csv')
    customer_static.to_csv(frame_path + 'customer_static.csv')

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

        self.finished_times = 0
        self.requested_times= 1
        self.declined_times = 0
        #print 'init~~~~~',self_vertex
        self.path = ([],[])

    def get_static_attributes(self):
        return {'w':self.w,'id' :G.vertex_index[self.self_vertex]}

    def get_dynamic_attributes(self):
        return {
            'id' :G.vertex_index[self.self_vertex],
            'position' : get_cross_position(self.self_vertex),
            'status' : self.status,
            'requested_times':self.requested_times,
            'declined_times':self.declined_times,
            'velocity' : get_road_current_speed(self.current_road),
            'finished_times':self.finished_times
        }

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
                    self.finished_times += 1

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

        def get_distance(s,e):
            pos_source = G.vertex_properties['position'][s]
            pos_target = G.vertex_properties['position'][e]
            return math.sqrt((pos_source[0] - pos_target[0])**2 + (pos_source[1] - pos_target[1])**2)

        available_v = []

        def recursive_add_vertex(vertex,deep_remain):
            if deep_remain == 0:
                return
            for v in vertex.out_neighbours():
                if v not in available_v:
                    available_v.append(v)
                    recursive_add_vertex(v,deep_remain-1)

        recursive_add_vertex(self.start_position,max_road_recursive)

        available_v = set(available_v)
        available_v.remove(self.start_position)

        self.target = available_v.pop()

        self.path = \
            gt.shortest_path(G_no_moving,self.start_position,self.target ,G.edge_properties['distance'])

        self.taxi = None
        self.self_vertex = self_vertex

        self.make_call()
        self.start_waiting = 0
        self.end_waiting = 0
        self.end_trip = 0

    def get_static_attributes(self):
        return {
            'id':G.vertex_index[self.self_vertex],
            'start_pos':G.vertex_index[self.start_position],
            'end_pos' :G.vertex_index[self.target]
        }

    def get_dynamic_attributes(self):
        taxi = None
        if self.taxi != None:
            taxi = G.vertex_index[self.taxi.self_vertex]
        return {
            'id':G.vertex_index[self.self_vertex],
            'taxi' : taxi ,
            'status' : self.status,
            'start_time':self.start_waiting,
            'start_waiting_time':self.end_waiting,
            'trip_end_time' : self.end_trip,
            'finihed':self.status == 'Finished'
        }

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
        self.start_waiting = current_time

    def set_on_trip(self):
        self.status = "OnTrip"
        self.end_waiting = current_time

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
        self.end_trip = current_time

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
