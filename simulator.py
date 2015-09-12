__author__ = 'coxious'

import random
from config import *
import graph_tool as gt
from entities import *
from core import *


taxies_list = []

def initialize():
    global taxies_list
    for i in xrange(taxi_amount):
        pos = random_vertex()
        v = add_taxi_vertex(pos)
        taxies_list.append(Taxi(pos,v))

def to_human_time(time):
    hour = int(time / 3600)
    minute = int((time - 3600 * hour)/60)
    second = time - 3600 * hour - 60 * minute
    return hour,minute,second

def update_graph():
    pass

def run_time_elapse(time):
    global taxies_list
    for taxi in taxies_list:
        taxi.run_time_elapse(time)

def run_strategy():
    pass

if __name__ == '__main__':
    plot_initialize()
    initialize()
    plot_window()
