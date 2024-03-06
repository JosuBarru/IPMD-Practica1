#!/usr/bin/env python

import os
from flask import Flask, jsonify
import requests

app = Flask(__name__)
app.json_sort_keys = False

def get_api_key():
    """
    Function to retrieve the API key from environment variables.
    """
    api_key = os.getenv("APIKEY")
    if not api_key:
        raise ValueError("Service not working")
    return api_key

AUTOPISTAS = ['A-1', 'AP-1', 'A-8', 'AP-68', 'A-15']
CIUDADES = ['BILBAO', 'DONOSTIA', 'VITORIA']
MAPPING = {
    'BILBAO': '48020',
    'DONOSTIA': '20069',
    'VITORIA': '01059'
}

@app.route('/test', methods=['GET'])
def test():
    return jsonify({"status": "OK"})

@app.route('/trafico/<autopista>', methods=['GET'])
def trafico(autopista):
    autopista = autopista.upper()
    if autopista in AUTOPISTAS:
        url = 'https://api.euskadi.eus/traffic/v1.0/incidences?_page=1'
        response = requests.get(url)
        data = response.json()
        # Return information of the selected highway.
        data = [x for x in data.get('incidences', []) if x['road'] == autopista]
        return jsonify(data)
    else:
        return jsonify({
            "mensaje": "No tengo datos de la autopista {}, limita tu consulta".format(autopista),
            "valores validos": AUTOPISTAS
        })

@app.route('/tiempo/<ciudad>', methods=['GET'])
def tiempo(ciudad):
    ciudad = ciudad.upper()
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
        # Return information about maximum and minimum temperatures.
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

if __name__ == "__main__":
    app.run()
