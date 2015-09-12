__author__ = 'coxious'

import simulator
import core
import time
from config import *

core.plot_initialize()
simulator.initialize()

#for time in xrange(24 * 3600):

def timed(f):
  ret = f()
  return ret, elapsed

for t in xrange(0,200,sec_per_cycle):

    start = time.time()
    #simulator.run_strategy()
    #simulator.update_graph()
    core.draw_cycle()
    simulator.run_time_elapse(t)
    elapsed = time.time() - start
    hour,minute,sec = simulator.to_human_time(t)
    print "Current Hour %d elapse %f\n"%(hour,elapsed)

#core.plot_window()
