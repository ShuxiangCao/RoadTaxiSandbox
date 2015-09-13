__author__ = 'coxious'

from config import *
from core import *
import math
from simulator import *
import graph_tool as gt
import numpy as np

def velocity(road_distance,car_count,road_type,t):

    #return 1000
    jamming_density = 135
    magnify_times =  8
    density = float(car_count) * magnify_times / road_distance
    max_vel = road_speed_dict[road_type]

    green_breg_prediction =  max_vel * math.log(jamming_density/density)
    underwood_prediction = max_vel * math.exp(- density / jamming_density)

    #print 'Greed %f underwood %f density %d jam %d\n' % \
    #      (green_breg_prediction,underwood_prediction,density,jamming_density)

    vel = min(green_breg_prediction , underwood_prediction)
    return vel / 3.6 # to m/s

def take_or_not(taxi,customer):

    road_speed_around_customer =\
        np.average([ get_road_current_speed(x) for x in customer.start_position.out_edges()])

    road_speed_max_around_customer =\
        np.average([ get_raod_max_speed(x) for x in customer.start_position.out_edges()])

    taxi_to_customer = gt.topology.shortest_distance(G_no_moving,taxi.self_vertex,customer.self_vertex)

    customer_trip_distance =\
        sum([ G.edge_properties['distance'][x] for x in customer.path[1]])

    def get_total_time(trip_distance,taxi_customer_distance,speed):
        return (trip_distance + taxi_customer_distance) * 1000 / speed

    def get_total_oil_cost(trip_distance,taxi_customer_distance,speed):
        return oil_cost_per_second * get_total_time(trip_distance,taxi_customer_distance,speed)

    def get_raw_profit(trip_distance,taxi_customer_distance,speed):
        return start_price + price_per_distance * trip_distance + \
             price_per_second * get_total_time(trip_distance,taxi_customer_distance,speed) \

    def get_profit(trip_distance,taxi_customer_distance,speed):
        return get_raw_profit(trip_distance,taxi_customer_distance,speed) - \
               get_total_oil_cost(trip_distance,taxi_customer_distance,speed)

    d_t = customer_trip_distance
    d_c = taxi_to_customer
    v = road_speed_around_customer
    v_max = road_speed_max_around_customer

    profit_value = (get_profit(d_t,d_c,v) + get_total_oil_cost(d_t,d_c,v)) / \
                   (get_profit(d_t,d_c,v_max) + get_total_oil_cost(d_t,d_c,v))

    confort_value = 1/math.sqrt(60) * math.sqrt(v)

    value_estimate = taxi.w * confort_value + (1 - taxi.w) * profit_value

    return value_estimate > 0.3
