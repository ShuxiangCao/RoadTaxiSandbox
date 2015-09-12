__author__ = 'coxious'

import simulator

for time in xrange(24 * 3600):
    simulator.run_strategy()
    simulator.update_graph()
    simulator.run_time_elapse(time)
    hour,minute,sec = simulator.to_human_time(time)
    print "Current Hour %d\n"%hour
