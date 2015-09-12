__author__ = 'coxious'

base_path = '/home/coxious/PycharmProjects/Taxi/shapefiles/'
available  = ['country','downtown','fast_road','highway','national','other','province']
road_color_dict = {
    'country' : 'black',
    'downtown' : 'darkred',
    'fast_road' : 'red',
    'highway' : 'dodgerblue',
    'national' : 'chocolate',
    'other' : 'gray',
    'province' : 'orange'
}
range_file = 'fast_road'

hdf_name = "Hangzhou_roads.h5"
table_name = 'Hangzhou'

graph_file_name = 'HangzhouGraph.gpickle'
graph_tool_file = 'Hangzhou.gt'
