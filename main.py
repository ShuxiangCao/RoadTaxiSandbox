__author__ = 'coxious'

import simulator
import core
import time
import entities
from config import *
import datetime

start = time.time()
print 'Initializing core...\n'
core.plot_initialize()
end = time.time()
print "Initializing core finished with %f\n"%(end - start)

start = time.time()
print 'Initializing simulator...\n'
simulator.initialize()
end = time.time()
print "Initializing simulator finished with %f\n"%(end - start)

#for time in xrange(24 * 3600):

for t in xrange(0,simulation_time,sec_per_cycle):

    start = time.time()
    #simulator.run_strategy()
    #simulator.update_graph()
    core.draw_cycle()
    draw_finish = time.time()
    simulator.run_time_elapse(t)
    calc = time.time() - draw_finish
    #hour,minute,sec = simulator.to_human_time(t)
    print "Cycle %d Draw %f calc %f\n"%(core.count,draw_finish-start,calc)

    remain_count = simulation_time / sec_per_cycle - core.count

#    print '\n'
    print 'estimated finish time %s\n'%\
          (datetime.datetime.now() + datetime.timedelta(seconds = remain_count * (time.time()-start))).isoformat(' ')
#    print '\n'

#core.plot_window()
entities.save_data()
#print entities.taxi_data