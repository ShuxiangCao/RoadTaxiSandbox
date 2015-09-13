__author__ = 'coxious'

import random
from config import *
import graph_tool as gt
from entities import *
from core import *
from multiprocessing import *
from multiprocessing import Pool as ThreadPool
import time
import numpy as np
import strategy
import pandas as pd


list_context = [ [] for x in range(thread_pool_size)]

def sync_par_list_run(f,list,thread_count):
    threads = []
    size = len(list)
    size_list = [size / thread_count ] * (thread_count -1)
    size_list.append(size - sum(size_list))

    manager = Manager()

    result_array = manager.list([])

    def worker(start,end,id):
        data = [ f(id,True) for i in xrange(start,end)]
        for x in data:
            list_context[id].append(x)

    current_start = 0
    for j in range(thread_count):
        #print current_start
        process = threading.Thread(target=worker, args=(current_start,current_start + size_list[j],j))
        current_start = current_start + size_list[j]
        process.start()
        threads.append(process)

    for thread in threads :
        thread.join()

    return result_array

def add_taxi(num):
    global taxies_list

    ws = np.random.normal(0.3,1./30,num)

    for i in xrange(num):
        pos = random_vertex()
        while G.vertex_properties['shape'][pos] == 'triangle':
            pos = random_vertex()

        v = add_taxi_vertex(pos)
        taxi = Taxi(pos,v,ws[i])
        taxies_list.append(taxi)

        dynamic_attributes = taxi.get_dynamic_attributes()
        data_frames['taxi%d'%G.vertex_index[v]] = pd.DataFrame(columns=dynamic_attributes.keys())

def add_customer(num,parallel = False):

    def add_one(id = 0,parallel = False):

        pos = get_random_station_pos()
        v = add_customer_vertex(pos)
        new_cos = Customer(pos,v)

        dynamic_attributes = new_cos.get_dynamic_attributes()
        data_frames['customer%d'%G.vertex_index[v]] = pd.DataFrame(columns=dynamic_attributes.keys())

        if parallel:
            return new_cos
        else:
            active_customer_list.append(new_cos)
            #print len(active_customer_list)

#    if parallel:
#        print "start parallel insert..."
#        pool = ThreadPool(thread_pool_size)
#        pool.map(add_one,xrange(num))
#        pool.close()
#        pool.join()
    if parallel:

        sync_par_list_run(lambda i,x: add_one(i,True),range(num),thread_pool_size)

        print list_context

        for i in list_context:
            for j in i:
                active_customer_list.append(j)
    else:
        for i in xrange(int(num)):
            add_one(i)

def initialize():
    add_taxi(taxi_amount)
    #add_customer(int(taxi_amount * target_full_rate),parallel=False)

def to_human_time(time):
    hour = int(time / 3600)
    minute = int((time - 3600 * hour)/60)
    second = time - 3600 * hour - 60 * minute
    return hour,minute,second

def run_taxi_test(i):
    taxies_list[i].run_time_elapse(0)

def run_time_elapse(t):
    global taxies_list

    global current_time
    entities.current_time = t
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

    add_customer(strategy.get_current_new_customer_num(t))

    customer_end = time.time()
    print 'Customer %f Taxi %f'%(customer_end - taxi_end,taxi_end - start)

    entities.statistics()

if __name__ == '__main__':
    def test(i):
        print i
        pass

    sync_par_list_run(test,[1,2,3,4,5],3)

