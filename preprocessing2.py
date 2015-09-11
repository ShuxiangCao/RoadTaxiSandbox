__author__ = 'coxious'

from config import *
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx

df = pd.read_hdf(base_path + hdf_name,table_name)
cross_road_dict = {}
G=nx.Graph()

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
            for neighbor in neighbors:
                G.remove_edge(neighbor,node)
            G.add_edge(neighbors[0],neighbors[1])
            G.remove_node(node)

def remove_single_edge():
    for u,v in G.edges():
        if G.degree(u) == 1 and G.degree(v) == 1:
            G.remove_edge(u,v)
            G.remove_node(u)
            G.remove_node(v)

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

print len(cross_road_dict)

print 'start build stations...'
build_station()
print 'start build graph...'
build_graph()
print 'removing middle nodes'
remove_middle_nodes()
print 'removing single edges'
remove_single_edge()
#print 'plotting graph'
#plot_graph()
print 'writing graph...'
nx.write_gpickle(G,base_path + graph_file_name)
print 'all finished...'


#station_x = []
#station_y = []
#for key in cross_road_dict.iterkeys():
#    station_x.append(key[0])
#    station_y.append(key[1])
#
#plt.scatter(station_x,station_y)

#print len(G.nodes())

#plt.show()
