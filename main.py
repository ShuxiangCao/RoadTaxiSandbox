__author__ = 'coxious'

import simulator
import core
import time
import entities
from config import *

core.plot_initialize()
simulator.initialize()

#for time in xrange(24 * 3600):

for t in xrange(0,7200,sec_per_cycle):

    start = time.time()
    #simulator.run_strategy()
    #simulator.update_graph()
    core.draw_cycle()
    draw_finish = time.time()
    simulator.run_time_elapse(t)
    calc = time.time() - draw_finish
    #hour,minute,sec = simulator.to_human_time(t)
    print "Cycle %d Draw %f calc %f\n"%(core.count,draw_finish-start,calc)

#core.plot_window()
entities.save_data()
#print entities.taxi_data