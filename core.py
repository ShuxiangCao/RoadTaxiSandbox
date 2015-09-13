__author__ = 'coxious'

from config import *
import graph_tool.all as gt
import random
import threading
import pandas as pd
import entities
import multiprocessing

G = gt.load_graph(base_path + graph_tool_file)

taxi_data = pd.DataFrame()

G_no_moving = G

inactive_vertex = []
count = 0

core_lock = threading.Lock()

def core_atomic_routine(f):
   # def func(*args, **kwargs):
   #     core_lock.acquire()
   #     val = f(*args, **kwargs)
   #     core_lock.release()
   #     return val
   # return func
   return f

@core_atomic_routine
def plot_initialize():
    color = G.new_vertex_property('vector<double>')
    shape = G.new_vertex_property('string')
    alive = G.new_vertex_property('bool')

    for v in G.vertices():
        color[v] = [254./255,238./255,107./255,1]
        shape[v] = 'circle'
        alive[v] = True

    G.vertex_properties['fillcolor'] = color
    G.vertex_properties['shape'] = shape
    G.vertex_properties['alive'] = alive

    global  G_no_moving
    G_no_moving = gt.GraphView(G,vfilt=lambda v: G.vertex_properties['shape'] == 'circle')
@core_atomic_routine
def add_inactive_vertex(vertex):
    G.vertex_properties['alive'][vertex] = False

@core_atomic_routine
def add_customer_vertex(position):

    customer_vertex = G.add_vertex()
    G.vertex_properties['fillcolor'][customer_vertex] = [182./255,65./255,69./255,1]
    G.vertex_properties['position'][customer_vertex] =\
        G.vertex_properties['position'][position]
    G.vertex_properties['shape'][customer_vertex] = 'square'
    G.vertex_properties['alive'][customer_vertex] = True

    return customer_vertex

@core_atomic_routine
def add_taxi_vertex(position):
    taxi_vertex = G.add_vertex()
    #change_taxi_color(taxi_vertex,True)
    G.vertex_properties['fillcolor'][taxi_vertex] = [182./255,222./255,110./255,1]
    G.vertex_properties['position'][taxi_vertex] =\
        G.vertex_properties['position'][position]
    G.vertex_properties['shape'][taxi_vertex] = 'triangle'
    G.vertex_properties['alive'][taxi_vertex] = True

    return taxi_vertex

@core_atomic_routine
def change_taxi_color(taxi_vertex,is_empty):
    if is_empty:
        G.vertex_properties['fillcolor'][taxi_vertex] = [182./255,222./255,110./255,1]
    else:
        G.vertex_properties['fillcolor'][taxi_vertex] = [182./255,65./255,69./255,1]

@core_atomic_routine
def update_taxi_position(taxi_vertex, pos):
    G.vertex_properties['position'][taxi_vertex] = pos


def get_cross_position(vertex):
    #print vertex
    return G.vertex_properties['position'][vertex]


def get_random_road_from_position(vertex):
    roads = [e for e in vertex.out_edges()]

    random.shuffle(roads)

    return roads[0]


def get_road_target(vertex,road):
    if road.source() == vertex:
        return road.target()
    else:
        return road.source()


def plot_window():
    gt.graph_draw(G, G.vertex_properties['position'],
                  vertex_shape=G.vertex_properties['shape'],
                  vertex_fill_color=G.vertex_properties['fillcolor'],
                  output=base_path + './frames/taxi%06d.png')

#def draw_cycle():
#    win.graph.regenerate_surface()
#    win.graph.queue_draw()
#    global  count
#    # if doing an offscreen animation, dump frame to disk
#    pixbuf = win.get_pixbuf()
#    pixbuf.savev(r'./frames/taxi%06d.png' % count, 'png', [], [])
#    count += 1

def draw_cycle():
    global count
    global  taxi_data

    series = pd.Series(entities.road_status_dict)
    taxi_data = taxi_data.append(series,ignore_index=True)

    def worker(Graph,current_count):

        U = gt.GraphView(Graph,vfilt=lambda v: Graph.vertex_properties['alive'][v])

        gt.graph_draw(U, U.vertex_properties['position'],
                 vertex_shape=U.vertex_properties['shape'],
                 vertex_fill_color=U.vertex_properties['fillcolor'],
                 output=frame_path + 'taxi%06d.png'%count,bg_color=(1,1,1,1),output_size=resolution)

    process = multiprocessing.Process(target=worker,args=(G.copy(),count))
    process.start()

    count += 1