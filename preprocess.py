__author__ = 'coxious'

from config import *
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import math
import graph_tool.all as gt

df = pd.read_hdf(base_path + hdf_name,table_name)
cross_road_dict = {}
G=nx.Graph()

Graph = gt.Graph(directed=False)

calc_distance = lambda u,v:math.sqrt((u[0] - v[0])**2 + (u[1] - v[1])**2)

vprop_position = Graph.new_vertex_property("vector<double>")
eprob_edge_type= Graph.new_edge_property("string")
eprob_edge_distance = Graph.new_edge_property("double")

cop_dict = {}

def push_to_dict(key,val,ext):
    if key in cross_road_dict:
        cross_road_dict[key].append([val,ext])
    else:
        cross_road_dict[key] = [val,ext]

def build_station():
    print df
    for row_tuple in df.iterrows():
        row = row_tuple[1]
        point_a = (row[0],row[1])
        point_b = (row[2],row[3])
        ext = row[4]
        push_to_dict(point_a,point_b,ext)
        push_to_dict(point_b,point_a,ext)

#        X = [point_a[0],point_b[0]]
#        Y = [point_a[1],point_b[1]]
#        plt.plot(X,Y)

def build_graph():
    for key in cross_road_dict.iterkeys():
        G.add_node(key)

    for row_tuple in df.iterrows():
        row = row_tuple[1]
        point_a = (row[0],row[1])
        point_b = (row[2],row[3])
        ext = row[4]
        G.add_edge(point_a,point_b)
        G[point_a][point_b]['type'] = ext

def remove_middle_nodes():
    for node in G.nodes():
        neighbors = G.neighbors(node)
        if len(neighbors) == 2:

            ext = G[node][neighbors[1]]['type']

            for neighbor in neighbors:
                G.remove_edge(neighbor,node)

            G.add_edge(neighbors[0],neighbors[1])
            G.remove_node(node)

            G[neighbors[0]][neighbors[1]]['type'] = ext

def remove_single_edge():
    for u,v in G.edges():
        if G.degree(u) == 1 and G.degree(v) == 1:
            G.remove_edge(u,v)
            G.remove_node(u)
            G.remove_node(v)

def convert_to_graph_tool():
    for node in G.nodes_iter():
        v = Graph.add_vertex()
        cop_dict[node] = v
        x = node[0]
        y = 500 - node[1]
        vprop_position[Graph.vertex(v)] = (x,y)

    for u,v in G.edges_iter():
        v1 = cop_dict[u]
        v2 = cop_dict[v]

        Graph.add_edge(v1,v2)

        eprob_edge_type[Graph.edge(v1,v2)] = G[u][v]['type']
        eprob_edge_distance[Graph.edge(v1,v2)] = calc_distance(u,v)
    Graph.edge_properties['type'] = eprob_edge_type
    Graph.edge_properties['distance'] = eprob_edge_distance
    Graph.vertex_properties['position'] = vprop_position

def save_largest_component():
    global Graph

    l = gt.label_largest_component(Graph)

    print l.a
    remove = []
    for x in xrange(len(l.a)):
        if l.a[x] == 0:
            remove.append(x)

    Graph.remove_vertex(remove)
    #u = gt.GraphView(Graph, vfilt=l)

    gt.remove_parallel_edges(Graph)

    Graph.save(base_path + graph_tool_file)

def plot_graph():
    X = []
    Y = []
    for node in G.nodes_iter():
        X.append(node[0])
        Y.append(node[1])

    plt.scatter(X,Y)

    for u,v in G.edges_iter():
        X = [u[0],v[0]]
        Y = [u[1],v[1]]
        plt.plot(X,Y)

def plot_graph_tool():
#    X = []
#    Y = []
#    for v in Graph.vertices():
#        node = vprop_position[Graph.vertex(v)]
#        X.append(node[0])
#        Y.append(node[1])
#
#    plt.scatter(X,Y)

    for v1,v2 in Graph.edges():
        u = vprop_position[Graph.vertex(v1)]
        v = vprop_position[Graph.vertex(v2)]
        X = [u[0],v[0]]
        Y = [u[1],v[1]]
        plt.plot(X,Y,color = road_color_dict[eprob_edge_type[Graph.edge(v1,v2)]])

print len(cross_road_dict)

print 'start build stations...'
build_station()
print 'start build graph...'
build_graph()
print 'removing middle nodes'
remove_middle_nodes()
print 'removing single edges'
remove_single_edge()
print 'converting to graph tool type...'
convert_to_graph_tool()
#print 'plotting graph'
#plot_graph_tool()
print 'writing graph...'
save_largest_component()
#nx.write_gpickle(G,base_path + graph_file_name)
print 'all finished...'

#station_x = []
#station_y = []
#for key in cross_road_dict.iterkeys():
#    station_x.append(key[0])
#    station_y.append(key[1])
#
#plt.scatter(station_x,station_y)

#print len(G.nodes())

plt.show()
