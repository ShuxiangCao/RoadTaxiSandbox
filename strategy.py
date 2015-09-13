__author__ = 'coxious'

from config import *
from core import *
import math
from simulator import *
import graph_tool as gt
import numpy as np
import entities

money_spend = 0

def get_current_new_customer_num(time):
    new_customer = 0

    if time < 2700:
        lamb = 2*2700 **2
    else:
        lamb = 2*4500**2

    return int(2 * math.exp( - (time - 2700)**2/lamb) * sec_per_cycle /2)

def velocity(road_distance,car_count,road_type,t):

    jamming_density = 135
    magnify_times =  20
    density = float(car_count) * magnify_times / road_distance
    max_vel = road_speed_dict[road_type]

    #green_breg_prediction =  max_vel * math.log(jamming_density/density)
    underwood_prediction = max_vel * math.exp(- density / jamming_density)

    #print 'Greed %f underwood %f density %d jam %d\n' % \
    #      (green_breg_prediction,underwood_prediction,density,jamming_density)

    vel = underwood_prediction#min(green_breg_prediction , underwood_prediction)
    return vel / 3.6 # to m/s

def take_or_not(taxi,customer):

    #return True

    road_speed_around_customer =\
        np.average([ entities.get_road_current_speed(x) for x in customer.start_position.out_edges()])

    road_speed_around_taxi =\
        np.average([ entities.get_road_current_speed(x) for x in taxi.last_pass_vertex.out_edges()])

    road_speed_max_around_customer =\
        np.average([ entities.get_raod_max_speed(x) for x in customer.start_position.out_edges()])

    road_speed_max_around_taxi =\
        np.average([ entities.get_raod_max_speed(x) for x in taxi.last_pass_vertex.out_edges()])

    taxi_to_customer = gt.topology.shortest_distance(G,source = taxi.last_pass_vertex, target = customer.start_position,
                                                     weights = G.edge_properties['distance'])

    #taxi_to_customer = sum([ G.edge_properties['distance'][x] for x in edge_path])
        #sum([ G.edge_properties['distance'][edge] for edge in edge_path])

    customer_trip_distance =\
        sum([ G.edge_properties['distance'][x] for x in customer.path[1]])

    def get_total_time(trip_distance,taxi_customer_distance,speed):
        return (trip_distance + taxi_customer_distance) * 1000 / speed

    def get_total_oil_cost(trip_distance,taxi_customer_distance,speed):
        return oil_cost_per_second * get_total_time(trip_distance,taxi_customer_distance,speed)

    def get_raw_profit(trip_distance,taxi_customer_distance,speed):
        profit = start_price + price_per_distance * trip_distance + \
             price_per_second * (trip_distance ) * 1000 / speed
        return profit

    def get_profit(trip_distance,taxi_customer_distance,speed):
        return get_raw_profit(trip_distance,taxi_customer_distance,speed) * 1.7 - \
               get_total_oil_cost(trip_distance,taxi_customer_distance,speed)

    #def price_to_value(d_t,d_c,v,price):
    #    return -1/( price + 1 + get_total_oil_cost(d_t,d_c,v) )+1

    def price_to_value(d_t,d_c,v,price):
        return (get_profit(d_t,d_c,v) + get_total_oil_cost(d_t,d_c,v)) /\
            (get_profit(3,0.5,v_max) + get_total_oil_cost(3,0.5,v_max))

    def confort_to_value(v,d_c):
        t = d_c * 1000/v
        lamb = 0.011512925464970227 / 2
        return math.exp(-lamb * t)

    d_t = 3
    d_c = 5
    v = road_speed_around_taxi
    v_max = road_speed_max_around_taxi
    lamb = 0.7
    x = len(entities.point_customer_dict[taxi.last_pass_vertex])

    #profit_value = -1/( get_profit(d_t,d_c,v) + 1 + get_total_oil_cost(d_t,d_c,v) )+1
    not_taken_profit = (-math.exp(-lamb * x ) + 1)*(get_profit(d_t,d_c,v_max)) + \
                    (math.exp(-lamb * x ) * get_total_oil_cost(d_t,d_c,v_max))

    profit_value = price_to_value(d_t,d_c,v_max,not_taken_profit)

    confort_value = confort_to_value(v_max,d_c)

    value_estimate_not_take = taxi.w * confort_value + (1 - taxi.w) * profit_value

    #if taxi_to_customer > 3:
    #    return False

    d_t = customer_trip_distance
    d_c = taxi_to_customer
    v = road_speed_around_customer
    v_max = road_speed_max_around_customer

    #profit_value = (get_profit(d_t,d_c,v) + get_total_oil_cost(d_t,d_c,v)) / \
    #               (get_profit(d_t,d_c,v_max) + get_total_oil_cost(d_t,d_c,v))


    profit_value = price_to_value(d_t,d_c,v,get_profit(d_t,d_c,v))

    money_used = get_raw_profit(d_t,d_c,v) * 0.7

    confort_value = confort_to_value(v,d_c)

    value_estimate_take = taxi.w * confort_value + (1 - taxi.w) * profit_value

    if value_estimate_take > value_estimate_not_take :

       # print '------------------'
       # print 'profit',get_profit(d_t,d_c,v)
       # print 'profit_value',profit_value
       # print 'confort value',confort_value
       # print 'w',taxi.w
       # print 'oil cost',get_total_oil_cost(d_t,d_c,v)
       # print 'not taken',not_taken_profit
       # print 'trip distance',d_t
       # print 'taxi customer distance',d_c
       # print 'total time',get_total_time(d_t,d_c,v)
       # print 'speed',v
       # #print [ G.edge_properties['distance'][x] for x in customer.path[1]]
       # print '------------------'

        global money_spend
        #print money_used
        money_spend = money_spend + money_used

    return value_estimate_take > value_estimate_not_take