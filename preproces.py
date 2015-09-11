__author__ = 'coxious'

import shapefile
import matplotlib.pyplot as plt
import pandas as pd

base_path = '/home/coxious/PycharmProjects/Taxi/shapefiles/'
available  = ['country','downtown','fast_road','highway','national','other','province']

cross_road_dict = {}
roads_dict = []

def push_to_dict(key,val):
    if key in cross_road_dict:
        cross_road_dict[key].append[val]
    else:
        cross_road_dict[key] = [val]

def get_range(file_name):
    sf = shapefile.Reader(base_path + file_name)
    shapes = sf.shapes()
    max_x = shapes[0].points[0][0]
    max_y = shapes[0].points[0][1]
    min_x = shapes[0].points[0][0]
    min_y = shapes[0].points[0][1]

    for shape in shapes:
        points = shape.points
        max_x = max(max_x,points[0][0],points[-1][0])
        max_y = max(max_y,points[0][1],points[-1][1])
        min_x = min(min_x,points[0][0],points[-1][0])
        min_y = min(min_y,points[0][1],points[-1][1])

    return (max_x,max_y,min_x,min_y)


def load_data(file_name,range):

    max_x,max_y,min_x,min_y = range

    sf = shapefile.Reader(base_path + file_name)
    shapes = sf.shapes()
    print len(shapes)
    for shape in shapes:
        points = shape.points
        if max_x != max(max_x,points[0][0],points[-1][0]) or \
            max_y != max(max_y,points[0][1],points[-1][1]) or  \
            min_x != min(min_x,points[0][0],points[-1][0]) or  \
            min_y != min(min_y,points[0][1],points[-1][1]):
            continue

#        X = [points[0][0],points[-1][0]]
#        Y = [points[0][1],points[-1][1]]
#        plt.plot(X,Y)

        point_a = points[0]
        point_b = points[-1]

        push_to_dict(point_a,point_b)
        push_to_dict(point_b,point_a)

        roads_dict.append([points[0][0],points[0][1],points[-1][0],points[-1][1],file_name])

range = get_range('fast_road')

for file in available:
    load_data(file,range)
print len(cross_road_dict)

df = pd.DataFrame(roads_dict)

df.to_hdf(base_path + "Hangzhou_roads.h5",'Hangzhou')

print df
