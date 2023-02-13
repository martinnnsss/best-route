# Importa las librerías necesarias
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from geopy.distance import great_circle
from sklearn.cluster import KMeans

# Carga los datos en un dataframe
df = pd.read_csv("direcciones.csv")

# Resuelve las direcciones en coordenadas geográficas
geolocator = Nominatim(user_agent="geoapiExercises")
df['coordinates'] = df['address'].apply(geolocator.geocode).apply(lambda x: (x.latitude, x.longitude))

# Calcula la distancia entre cada par de direcciones
distances = []
for i in range(len(df)):
    for j in range(i+1, len(df)):
        distances.append((i, j, great_circle(df.iloc[i]['address'], df.iloc[j]['address']).m))

# Crea una matriz con las distancias
X = np.zeros((len(df), len(df)))
for i, j, d in distances:
    X[i, j] = d
    X[j, i] = d

# Inicializa el modelo KMeans con n_clusters=1
kmeans = KMeans(n_clusters=1)

# Ajusta el modelo a la matriz
kmeans.fit(X)

# Asigna etiquetas a cada punto de datos
df['label'] = kmeans.labels_

# Continúa agrupando hasta que cada clúster tenga 4 o menos direcciones
while df.groupby('label').agg({'address':'count'}).max().values[0] > 4:
    kmeans.n_clusters += 1
    kmeans.fit(X)
    df['label'] = kmeans.labels_

# Verifica los resultados
print(df.groupby('label').agg({'address':'count'}))

# Imprime el resultado
print(df)