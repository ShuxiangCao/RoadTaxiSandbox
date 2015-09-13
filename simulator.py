__author__ = 'coxious'

import random
from config import *
import graph_tool as gt
from entities import *
from core import *
from multiprocessing import Process
from multiprocessing.dummy import Pool as ThreadPool
import time
import numpy as np

active_customer_list = []
taxies_list = []

current_time = 0


def sync_par_list_run(f,list,thread_count):
    threads = []
    size = len(list)
    size_list = [size / thread_count ] * (thread_count -1)
    size_list.append(size - sum(size_list))

    def worker(start,end):
        for i in xrange(start,end):
            f(i)

    current_start = 0
    for j in range(thread_count):
        #print current_start
        process = Process(target=worker, args=(current_start,current_start + size_list[j]))
        current_start = current_start + size_list[j]
        process.start()
        threads.append(process)

    for thread in threads :
        thread.join()

def add_taxi(num):
    global taxies_list

    ws = np.random.normal(0.3,1./30,num)

    for i in xrange(num):
        pos = random_vertex()
        while G.vertex_properties['shape'][pos] == 'triangle':
            pos = random_vertex()

        v = add_taxi_vertex(pos)
        #print v
        taxies_list.append(Taxi(pos,v,ws[i]))

def add_customer(num):

    def add_one(i):
        pos = get_random_station_pos()
        v = add_customer_vertex(pos)
        active_customer_list.append(Customer(pos,v))

    for i in xrange(num):
        add_one(i)
    #pool = ThreadPool(thread_pool_size)
    #pool.map(add_one,xrange(num))
    #pool.close()
    #pool.join()

def initialize():
    add_taxi(taxi_amount)

    #add_taxi(1)

def to_human_time(time):
    hour = int(time / 3600)
    minute = int((time - 3600 * hour)/60)
    second = time - 3600 * hour - 60 * minute
    return hour,minute,second

def update_graph():
    pass

def run_taxi_test(i):
    taxies_list[i].run_time_elapse(0)

def run_time_elapse(t):
    global taxies_list

    global current_time
    current_time = t

    start = time.time()
    for taxi in taxies_list:
        taxi.run_time_elapse(current_time)


   # pool = ThreadPool(thread_pool_size)
   # pool.map(run_taxi_test,xrange(len(taxies_list)))

   # pool.close()
   # pool.join()

    taxi_end = time.time()
    #pool.map(lambda taxi:taxi.run_time_elapse(current_time),taxies_list)
    #sync_par_list_run(,taxies_list,8)

    add_customer(new_customer_per_cycle)

    customer_end = time.time()
    print 'Customer %f Taxi %f'%(customer_end - taxi_end,taxi_end - start)

def run_strategy():
    pass

if __name__ == '__main__':
    def test(i):
        print i
        pass

    sync_par_list_run(test,[1,2,3,4,5],3)

