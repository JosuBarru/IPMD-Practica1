#!/usr/bin/env python

# Usando las APIS de OpenData Euskadi y AEMET, ofrecer usando una aplicación Python+Flask un servicio web con 
# esta API REST simplificada: 
# GET /test Resultado: mensaje de OK si el servidor está operativo. 
# GET /trafico/{autopista} donde {autopista} puede tomar los valores 'A-1', 'AP-1', 'A-8', 'AP-68', 'A-15' (tanto en 
# mayúsculas como en minúsculas). 
# Resultado: el último parte de incidencias de tráfico en la autopista seleccionada, o un mensaje de error si no se 
# indica una autopista de la lista. El mensaje de error debe informar de los valores permitidos. 
# GET /tiempo/{ciudad} donde {ciudad} puede tomar los valores "Bilbao", "Donostia", "Vitoria" (en cualquier 
# configuración de mayúsculas/minúsculas). 
# Resultado: la última predicción de temperaturas máximas y mínimas para la ciudad seleccionada, o un mensaje de 
# error si no se indica una ciudad de la lista. El mensaje de error debe informar de los valores permitidos.

# Consideraciones importantes:  
# 1. 
# El servidor web integrado en Flask es solo para pruebas, no está recomendado para servicios en producción. 
# Una vez superadas las pruebas, hay que usar un servidor basado en gunicorn o en waitress (este último es más 
# sencillo de poner en marcha).  
# 2. 
# El servicio /trafico obtendrá los datos usando la API de tráfico de Open Data Euskadi. En concreto 
# https://api.euskadi.eus/traffic/v1.0/incidences?_page=1. Esta API no requiere ningún tipo de "api_key".  
# 3. 
# El servicio /tiempo está basado en la API de AEMET. En concreto en  
# https://opendata.aemet.es/opendata/api/prediccion/especifica/municipio/diaria/.... Para usarlo es necesario 
# disponer de una "api_key". La solución debe incorporar formas de gestionar posibles cambios en esta "api_key" 
# sin necesidad de modificar programas o rehacer imágenes.  
# 4. 
# Los valores devueltos por la API deben estar en formato JSON bien formado.  


from flask import Flask, jsonify, request

import requests
from config import apikey


app = Flask(__name__)

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"status": "OK"})

@app.route('/trafico/<autopista>', methods=['GET'])
def trafico(autopista):
    autopistas = ['A-1', 'AP-1', 'A-8', 'AP-68', 'A-15']
    autopista = autopista.upper()
    if autopista in autopistas:
        url = 'https://api.euskadi.eus/traffic/v1.0/incidences?_page=1'
        response = requests.get(url)
        data = response.json()
        print(data)
        # devuelveme la informacion de la autopista seleccionada.   
        data = [x for x in data['incidences'] if x['road'] == autopista]
        return jsonify(data)
    else:
        return jsonify({"error": "Autopista no valida"})


@app.route('/tiempo/<ciudad>', methods=['GET'])
def tiempo(ciudad):
    ciudad = ciudad.upper()
    ciudades = ['BILBAO', 'DONOSTIA', 'VITORIA']
    if ciudad in ciudades:
        url = 'https://opendata.aemet.es/opendata/api/prediccion/especifica/municipio/diaria/' + ciudad
        headers = {
            'accept': 'application/json',
            'api_key': apikey
        }
        response = requests.get(url, headers=headers)
        data = response.json()
        return jsonify(data)
    else:
        return jsonify({"error": "Ciudad no valida"})
    
