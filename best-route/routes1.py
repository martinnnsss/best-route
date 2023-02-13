import pandas as pd
from geopy.geocoders import Nominatim
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# Carga tu dataframe
df = pd.read_csv('ruta/a/tu/archivo.csv')

# Crea una instancia del geocodificador
geolocator = Nominatim(user_agent="myGeocoder")

# Convierte las direcciones en coordenadas geográficas
df['latitude'] = df['address'].apply(lambda x: geolocator.geocode(x).latitude)
df['longitude'] = df['address'].apply(lambda x: geolocator.geocode(x).longitude)

# Crea una matriz numpy para alimentar al modelo de agrupamiento
X = df[['latitude', 'longitude']].values

# Aplica el método del codo para determinar el número óptimo de clústeres
SSE = []
for cluster in range(1,20):
    kmeans = KMeans( n_clusters = cluster, init='k-means++')
    kmeans.fit(X)
    SSE.append(kmeans.inertia_)

# Convervtiendo la lista en el dataframe para visualizar fácilmente
frame = pd.DataFrame({'Cluster':range(1,20), 'SSE':SSE})

# Graficando el método del codo
plt.figure(figsize=(12,6))
plt.plot(frame['Cluster'], frame['SSE'], marker='o')
plt.xlabel('Número de clústeres')
plt.ylabel('SSE')

# Encuentra el punto de inflexión en el gráfico
for i in range(1, len(SSE)-1):
    if SSE[i]>=SSE[i-1] and SSE[i]>=SSE[i+1]:
        optimal_clusters = i+1
        break

# Crea una instancia del modelo KMeans con el número óptimo de clústeres
kmeans = KMeans(n_clusters=optimal_clusters)
# Ajusta el modelo de agrupamiento a la matriz
kmeans.fit(X)

# Asigna etiquetas a cada punto de datos
df['label'] = kmeans.labels_

# Agrupa los datos por etiqueta y contar la cantidad de direcciones en cada clúster
df_grouped = df.groupby('label').agg({'address':'count'})

# Filtra los clústeres con más de 4 direcciones
df_filtered = df_grouped[df_grouped['address'] <= 4]

# Reasigna etiquetas a los puntos de datos en los clústeres filtrados
df.loc[df['label'].isin(df_filtered.index), 'label'] = -1

# Reentrena el modelo KMeans con las etiquetas reasignadas
kmeans = KMeans(n_clusters=len(df_filtered))
kmeans.fit(X)
df['label'] = kmeans.labels_

# Verifica los resultados
print(df_grouped)

