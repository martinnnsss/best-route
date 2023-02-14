import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from geopy.distance import great_circle
from sklearn.cluster import KMeans
import re


import warnings
warnings.filterwarnings("ignore")


data = pd.read_csv(r'C:\Users\martin.olivares\Desktop\projects\best-route\test_3.csv')

df=pd.DataFrame()
df['address']=data['Direccion de inicio']
df['recogida']=data['Hora de recogida']
df['destino']=data['Dirección destino']


geolocator = Nominatim(user_agent="geoapiExercises")

grouped = df.groupby("recogida")

for name, group in grouped:

    # Calcula la distancia entre cada par de direcciones
    X = np.zeros((len(group), len(group)))
    for i in range(len(group)):
        address1 = group.iloc[i]['address']
        loc1 = geolocator.geocode(address1)
        lat1, lon1 = loc1.latitude, loc1.longitude
        point1 = (lat1, lon1)
        for j in range(i+1, len(group)):
            address2 = group.iloc[j]['address']
            loc2 = geolocator.geocode(address2)
            lat2, lon2 = loc2.latitude, loc2.longitude
            point2 = (lat2, lon2)
            X[i, j] = great_circle(point1, point2).m
            X[j, i] = great_circle(point1, point2).m

    # Crea una matriz con las distancias
    kmeans = KMeans(n_clusters=1)
    kmeans.fit(X)
    group['label'] = kmeans.labels_

    # Continúa agrupando hasta que cada clúster tenga 4 o menos direcciones
    while group.groupby('label').agg({'address':'count'}).max().values[0] > 4:
        kmeans.n_clusters += 1
        kmeans.fit(X)
        group['label'] = kmeans.labels_
    df.loc[group.index, "label"] = group["label"]