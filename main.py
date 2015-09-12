__author__ = 'coxious'

import simulator
import core
import time

core.plot_initialize()
simulator.initialize()
#for time in xrange(24 * 3600):
def timed(f):
  start = time.time()
  ret = f()
  elapsed = time.time() - start
  return ret, elapsed

for t in xrange(10):
    #simulator.run_strategy()
    #simulator.update_graph()
    ret,elapsed = timed(lambda : simulator.run_time_elapse(t))
    print elapsed
    hour,minute,sec = simulator.to_human_time(t)
    print "Current Hour %d\n"%hour

core.plot_window()
