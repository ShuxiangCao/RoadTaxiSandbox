__author__ = 'coxious'

from config import *
import math

def velocity(road_distance,car_count,road_type):

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
