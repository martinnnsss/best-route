import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from geopy.distance import great_circle
from sklearn.cluster import KMeans

data = pd.read_csv(r'C:\Users\martin.olivares\Desktop\projects\best-route\test_2.csv')

df=pd.DataFrame()
df['address']=data['Direccion de inicio']
df['recogida']=data['Hora de recogida']


#Función para verificar que las direcciones estén correctas. Posteriormente se dejan fuera las incorrectas (momentaneo)

def correct_address(address):
    geolocator = Nominatim(user_agent="geoapiExercises")
    location = geolocator.geocode(address)
    if location:
        return location.address
    else:
        return 'no_existe_la_direccion'


df['corrected_address'] = df['address'].apply(correct_address)


filter=df['corrected_address']!='no_existe_la_direccion'
filter2= df['address']!='PASAJE CERO 14 CHORRILLOS, VIÑA DEL MAR'
df.where(filter & filter2,inplace=True)
df.dropna(inplace=True)


#crea coordenadas geográficas
geolocator = Nominatim(user_agent="geoapiExercises")

# Calcula la distancia entre cada par de direcciones
distances = []
for i in range(len(df)):
    address1 = df.iloc[i]['address']
    loc1 = geolocator.geocode(address1)
    lat1, lon1 = loc1.latitude, loc1.longitude
    point1 = (lat1, lon1)
    for j in range(i+1, len(df)):
        address2 = df.iloc[j]['address']
        loc2 = geolocator.geocode(address2)
        lat2, lon2 = loc2.latitude, loc2.longitude
        point2 = (lat2, lon2)
        distances.append((i, j, great_circle(point1, point2).m))

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