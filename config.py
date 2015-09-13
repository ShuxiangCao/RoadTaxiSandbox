__author__ = 'coxious'

# Program
base_path = '/home/coxious/PycharmProjects/Taxi/shapefiles/'
frame_path = '/home/coxious/PycharmProjects/Taxi/frames/'
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

road_speed_dict= {
    'country' : 60,
    'downtown' : 60,
    'fast_road' : 80,
    'highway' : 100,
    'national' : 80,
    'other' : 40,
    'province' : 60
}

range_file = 'fast_road'

hdf_name = "Hangzhou_roads.h5"
table_name = 'Hangzhou'

graph_file_name = 'HangzhouGraph.gpickle'
graph_tool_file = 'Hangzhou.gt'

resolution = (4800 , 4800)

thread_pool_size = 8
sec_per_cycle = 10

#Strategy
taxi_amount = 6000
new_customer_per_cycle = 55

price_per_distance = 2.5
price_per_second = 36. /3600
oil_cost_per_second = 38.4 /3600
start_price = 4.5
