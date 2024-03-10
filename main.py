#!/usr/bin/env python

import os
from flask import Flask, jsonify
import requests

app = Flask(__name__)  # Crea una instancia de la aplicación Flask
app.json_sort_keys = False  # Desactiva la ordenación de claves al devolver JSON

# Función para obtener la clave de la API desde las variables de entorno
def get_api_key():
    """
    Function to retrieve the API key from environment variables.
    """
    api_key = os.getenv("APIKEY")
    if not api_key:
        raise ValueError("Service not working")
    return api_key

# Listas de autopistas y ciudades
AUTOPISTAS = ['A-1', 'AP-1', 'A-8', 'AP-68', 'A-15']
CIUDADES = ['BILBAO', 'DONOSTIA', 'VITORIA']

# Mapeo de ciudades a códigos de municipios
MAPPING = {
    'BILBAO': '48020',
    'DONOSTIA': '20069',
    'VITORIA': '01059'
}

# Ruta para verificar el estado del servicio
@app.route('/test', methods=['GET'])
def test():
    return jsonify({"status": "OK"})

# Ruta para obtener información sobre el tráfico en una autopista específica
@app.route('/trafico/<autopista>', methods=['GET'])
def trafico(autopista):
    autopista = autopista.upper()  # Convertir a mayúsculas para evitar problemas de casos
    if autopista in AUTOPISTAS:
        url = 'https://api.euskadi.eus/traffic/v1.0/incidences?_page=1'
        response = requests.get(url)
        data = response.json()
        # Filtrar información de la autopista seleccionada
        data = [x for x in data.get('incidences', []) if x['road'] == autopista]
        return jsonify(data)
    else:
        return jsonify({
            "mensaje": "No tengo datos de la autopista {}, limita tu consulta".format(autopista),
            "valores validos": AUTOPISTAS
        })

# Ruta para obtener información sobre el tiempo en una ciudad específica
@app.route('/tiempo/<ciudad>', methods=['GET'])
def tiempo(ciudad):
    ciudad = ciudad.upper()  # Convertir a mayúsculas para evitar problemas de casos
    if ciudad in CIUDADES:
        api_key = get_api_key()
        url = 'https://opendata.aemet.es/opendata/api/prediccion/especifica/municipio/diaria/' + MAPPING[ciudad]
        headers = {
            'accept': 'application/json',
            'api_key': api_key
        }
        response = requests.get(url, headers=headers)
        data = response.json()
        data = requests.get(data.get('datos', ''))
        # Obtener información sobre las temperaturas máximas y mínimas
        data = data.json()
        max_temp = data[0]['prediccion']['dia'][0]['temperatura']['maxima']
        min_temp = data[0]['prediccion']['dia'][0]['temperatura']['minima']
        data = {
            'mensaje': "Prevision de temperaturas en " + ciudad,
            'maxima': max_temp,
            'minima': min_temp
        }
        return jsonify(data)
    else:
        return jsonify({"error": "Ciudad no valida"})

# Inicia la aplicación Flask si este script se ejecuta directamente
if __name__ == "__main__":
    app.run()
