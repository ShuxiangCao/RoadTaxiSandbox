__author__ = 'coxious'

import matplotlib.pyplot as plt

import pandas as pd
from config import *

data_dict = {}

data_dict['ori'] = pd.read_csv(csv_path + "origin.csv",header = 0)
data_dict['p15'] = pd.read_csv(csv_path + "plus15.csv",header = 0)
data_dict['t17'] = pd.read_csv(csv_path + "times1point7.csv",header = 0)

type_to_description = {
    'ori' : "no extra fee",
    'p15' : "15 yuan each ride",
    't17' : "get 1.7 times profit"
}

#print ori

X = [ x * sec_per_cycle for x in data_dict['ori'].index.values ]

names = [ 'on_trip_count','money_spent','taxi_free_rate',	'average_decline_rate'	,'waiting_customers'	,
          'highest_decline_rate'	,'no_response_call'	,'lowest_decline_rate',	'total_call',	'averange_speed',
          'no_response_rate',	'finished_count'	,'average_waiting_time']

y_axies = ['ride count',"Yuan","%","%","person count","%","ride count","%","ride count","m/s","%","ride count","s"]

y_axies_dict = {}

for i in range(len(names)):
    y_axies_dict[names[i]] = y_axies[i]

def plot_type(types,column):
    name = column.replace('_',' ')
    plt.figure(name)
    plt.title(name)
    plt.xlabel("Time (s)")
    for d in types:
        try:
            Y = data_dict[d][column].values
            plt.plot(X,Y,label = type_to_description[d])
            plt.legend()
            #plt.plot(X,Y)
        except:
            pass
        plt.ylabel(y_axies_dict[column])

all_type = ['ori','p15','t17']

for x in names:
    plot_type(all_type,x)

plt.show()
