import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from geopy.distance import great_circle
from scipy.spatial.distance import cdist
from sklearn.cluster import KMeans
import re



data = pd.read_csv(r'C:\Users\martin.olivares\Desktop\projects\best-route\test_3.csv')

df=pd.DataFrame()
df['address']=data['Direccion de inicio']
df['hora_recogida']=data['Hora de recogida']
df['destino']=data['Dirección destino']

geolocator = Nominatim(user_agent="geoapiExercises")

grouped = df.groupby("hora_recogida")

for name, group in grouped:
    if len(group) > 1:
        # Calcula la distancia entre cada par de direcciones de recogida y destino
        X = np.zeros((len(group), len(group)))
        X_destino = np.zeros((len(group), len(group)))
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
                address3 = group.iloc[j]['destino']
                loc3 = geolocator.geocode(address3)
                lat3, lon3 = loc3.latitude, loc3.longitude
                point3 = (lat3, lon3)
                X_destino[i, j] = great_circle(point1, point3).m
                X_destino[j, i] = great_circle(point2, point3).m
        
        # Crea una matriz con las distancias de recogida y destino
        X_final = np.concatenate((X, X_destino), axis=1)
        X_final = np.concatenate((X_final, np.concatenate((np.transpose(X), np.transpose(X_destino)), axis=1)), axis=0)

        kmeans = KMeans(n_clusters=1)
        kmeans.fit(X_final)
        distances = cdist(X_final[kmeans.labels_ == 0], kmeans.cluster_centers_)
        cluster_labels = np.argmin(distances, axis=1)
        
        while np.unique(cluster_labels).size < kmeans.n_clusters:
            kmeans.n_clusters -= 1
            distances = cdist(X_final[kmeans.labels_ == 0], kmeans.cluster_centers_)
            cluster_labels = np.argmin(distances, axis=1)
            # Obtener dirección, destino y etiqueta de cada grupo
        for idx, label in enumerate(np.unique(cluster_labels)):
            addresses = list(group.iloc[cluster_labels == label]['address'])
            destino = list(group.iloc[cluster_labels == label]['destino'])[0]
            print(f"Grupo {idx + 1} - Direcciones: {addresses}, Destino: {destino}, Etiqueta: {label}")