__author__ = 'coxious'

from config import *
import graph_tool.all as gt

G = gt.load_graph(base_path + graph_tool_file)


def plot_initialize():
    color = G.new_vertex_property('double')
    shape = G.new_vertex_property('string')

    for v in G.vertices():
        color[v] = 0.6
        shape[v] = 'circle'

    G.vertex_properties['fillcolor'] = color
    G.vertex_properties['shape'] = shape


def add_taxi_vertex(position):
    taxi_vertex = G.add_vertex()
    G.vertex_properties['fillcolor'][taxi_vertex] = 0.3
    G.vertex_properties['position'][taxi_vertex] =\
        G.vertex_properties['position'][position]
    G.vertex_properties['shape'][taxi_vertex] = 'triangle'


def update_taxi_position(taxi_vertex, pos):
    G.vertex_properties['position'][taxi_vertex] = pos


def get_cross_position(vertex):
    return G.vertex_properties['position'][vertex]


def plot_window():
    gt.graph_draw(G, G.vertex_properties['position'],
                  vertex_shape=G.vertex_properties['shape'],
                  vertex_fill_color=G.vertex_properties['fillcolor'],
                  output=base_path + "test.pdf")
