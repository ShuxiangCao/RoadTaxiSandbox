__author__ = 'coxious'

from config import *
import graph_tool.all as gt
import random
from gi.repository import Gtk, Gdk, GdkPixbuf, GObject

G = gt.load_graph(base_path + graph_tool_file)

offscreen = False


count = 0
win = None


def plot_initialize():
    color = G.new_vertex_property('double')
    shape = G.new_vertex_property('string')

    for v in G.vertices():
        color[v] = 0.6
        shape[v] = 'circle'

    G.vertex_properties['fillcolor'] = color
    G.vertex_properties['shape'] = shape

#    global win
#    win = Gtk.OffscreenWindow()
#    win.set_default_size(1920, 1080)
#    win.graph = gt.GraphWidget(G, G.vertex_properties['position'],
#                  vertex_shape=G.vertex_properties['shape'],
#                  vertex_fill_color=G.vertex_properties['fillcolor'],
#                  )
#    win.add(win.graph)
#    win.connect("delete_event", Gtk.main_quit)
#    win.show_all()

def add_taxi_vertex(position):
    taxi_vertex = G.add_vertex()
    G.vertex_properties['fillcolor'][taxi_vertex] = 0.3
    G.vertex_properties['position'][taxi_vertex] =\
        G.vertex_properties['position'][position]
    G.vertex_properties['shape'][taxi_vertex] = 'triangle'

    return taxi_vertex


def update_taxi_position(taxi_vertex, pos):
    G.vertex_properties['position'][taxi_vertex] = pos


def get_cross_position(vertex):
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
#
#    # if doing an offscreen animation, dump frame to disk
#    pixbuf = win.get_pixbuf()
#    pixbuf.savev(r'./frames/taxi%06d.png' % count, 'png', [], [])
#    count += 1

def draw_cycle():
     global  count
     gt.graph_draw(G, G.vertex_properties['position'],
                  vertex_shape=G.vertex_properties['shape'],
                  vertex_fill_color=G.vertex_properties['fillcolor'],
                  output=frame_path + 'taxi%06d.png'%count,bg_color=(1,1,1,1),output_size=resolution)
     count += 1
