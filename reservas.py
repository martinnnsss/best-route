import pandas as pd
import requests as re
import json
from bs4 import BeautifulSoup
from pprint import pprint
from googleapiclient import discovery
import time
from time import sleep
import openpyxl as pxl
import pygsheets as pg
import tkinter
import tkinter.filedialog
#%%

def find_path(root_):
    f = tkinter.filedialog.askopenfilename(
        parent=root_, initialdir='..',
        title='Choose file',
        filetypes=[("Excel file", "*.xlsx"), ("Excel file", "*.csv")]
    )
    print(f)
    return f

root = tkinter.Tk()
documento = find_path(root)
root.destroy()

print("Carga de archivo completado")

#%%
​
toploc = pd.read_excel(documento, sheet_name='Sheet1')
toploc.fillna('',inplace=True)
toploc
#%%
#diccionario de productos Corp con sus product_id
products_corp = {
  'Cabify Group (8 pax)':'7c992d24e7749a846630a124860d94f8',
  'Cabify Group (6 pax)':'e3322715fa956f714d484c5cff2bce5a',
  'Cabify Corp':'a9a7147c8194110c05790222b11b9062',
  'Cabify Mix Corp':'3b0db061edbafd1eccb7dd343daa72b6',
  'Taxi Corp':'ae3c9faa76a750592c9cbe8f2146b5e1'
}
​
#%%
#Se colocan los product_id de cada ruta
product_id = []
for p, r in zip(toploc['Producto'],toploc['Ruta']):
  for d, v in zip(products_corp,products_corp.values()):
    if p in d:  
      product_id.append(v)
         
​
toploc['product_id'] = product_id
​
​
# %%
#FUNCION DE GEOCODING:
def coordenadas(dir):
  #se usa la api geocoding de google.
  #Hay que remplazar espacios por %20
​
  key = 'AIzaSyAvTzCycvOetN-NA51GNqxb80d-Ma-0Azg'
  url = 'https://maps.googleapis.com/maps/api/geocode/json?address={}&region=cl&key={}'.format(dir.replace(" ","%20").replace(",",""),key)
  geo_info = re.request("post",url)
  geo_info.json()
  lat = geo_info.json()['results'][0]['geometry']['location']['lat']
  lon = geo_info.json()['results'][0]['geometry']['location']['lng']
​
  return lat,lon
​
lat_i,lon_i,lat_f,lon_f = [], [], [], []
​
for i, f in zip(toploc['Direccion de inicio'],toploc['Dirección destino']):
  
  #se usa funcion de geocoding
  coor_i = coordenadas(i)
  lat_i.append(coor_i[0])
  lon_i.append(coor_i[1])
​
  coor_f = coordenadas(f)
  lat_f.append(coor_f[0])
  lon_f.append(coor_f[1])
​
toploc['latitud de inicio'],toploc['longitud de inicio'], toploc['latitud de fin'], toploc['longitud de fin'] = lat_i, lon_i, lat_f, lon_f
​
print("Coordenadas extraídas")
​
#%%
​
#Función para el Token de cliente de Cabify
​
secret = pd.read_excel(documento,sheet_name='token')
secret
​
def Cabify_Token(client,c_secret):
​
  #Credenciales de la Api
​
  client_id = client
  client_secret = c_secret
​
  url = 'https://cabify.com/auth/api/authorization?grant_type=client_credentials&client_id={}&client_secret={}'.format(client_id,client_secret)
​
  payload={}
  headers = {}
​
  response = re.request("POST", url, headers=headers, data=payload).json()
​
  #Token tipo Bearer
  token = response['access_token']
​
  return token
​
​
#%%
​
token = Cabify_Token(secret['client_id'][0],secret['client_secret'][0])
token
​
headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": "Bearer {}".format(token)
}
url = "https://cabify.com/api/v4/journey"
​
​
#%%
​
rutas = toploc['Ruta'].unique()
payload=[]
​
for r in rutas:
  trip = toploc[toploc['Ruta']==r].reset_index()
  trip
​
​
  #Dividimos el json de las paradas en 2 partes, Solicitante y Paradas
  
  sol = {
    "message": "Viaje con "+str(len(trip))+" paradas"+"\n" + trip['Instrucciones'][0],
    "product_id": trip['product_id'][0],
    "requester_id": trip['Solicitante'][0],
    "rider": {
      "email": trip['Mail_Pasajero'][0],
      "locale": "CL",
      "mobile": {
        "mobile_cc": str(trip['Telefono de contacto'][0])[0:2],
        "mobile_num": str(trip['Telefono de contacto'][0])[2:],
        "id":trip['Solicitante'][0]
      },
      "name": trip['Nombre de pasajero'][0]
    },
    "start_at": trip['Fecha'][0]+" "+trip['Hora de recogida'][0],
  }
​
  paradas = [{
            "addr": trip['Direccion de inicio'][0],
            "city": "Santiago",
            "contact": {
                "mobile_cc": str(trip['Telefono de contacto'][0])[0:2],
                "mobile_num": str(trip['Telefono de contacto'][0])[2:],
                "name": trip['Nombre de pasajero'][0]
            },
            "country": "CL",
            "loc": [trip['latitud de inicio'][0], trip['longitud de inicio'][0]],
            "instr":trip['Instrucciones'][0] 
        },{
          "addr": trip['Dirección destino'][0],
          "city": "Santiago",
          "contact": {
              "mobile_cc": str(trip['Telefono de contacto'][0])[0:2],
              "mobile_num": str(trip['Telefono de contacto'][0])[2:],
              "name": trip['Nombre de pasajero'][0]
          },
          "country": "CL",
          "loc": [trip['latitud de fin'][0], trip['longitud de fin'][0]],
          "instr":trip['Instrucciones'][0] 
​
        }
        ]
​
  for lat_f, lon_f,dir_f,nom,i,inst in zip(trip['latitud de fin'],trip['longitud de fin'],trip['Dirección destino'],trip['Nombre de pasajero'],trip.index,trip['Instrucciones']):
    if i != 0:
      paradas.append({
              "addr": dir_f,
              "city": "Santiago",
              "contact": {
                  "mobile_cc": str(trip['Telefono de contacto'][0])[0:2],
                  "mobile_num": str(trip['Telefono de contacto'][0])[2:],
                  "name": nom
              },
              "country": "CL",
              "loc": [lat_f, lon_f],
              "instr":inst
          })
    else:
      continue
    
    #Se agrega al diccionario sol, las paradas
  
  sol['stops'] = paradas
    
  payload.append(sol)
​
​
#%%
#Se crean las reservas haciendo el Request a la API Rest pública
​
try:
  for pay in payload:
    response = re.post(url, json=pay, headers=headers)
​
    print(response.text)
  
  input('Presione ENTER para continuar')
​
except:
  input('Presione ENTER para continuar')
​