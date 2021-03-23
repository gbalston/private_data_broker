from flask import Flask, jsonify
import json
import requests
import base64

app=Flask(__name__)

def encode_int(x):
    return base64.b64encode(str(x).encode()).decode()

def decode_int(x):
    return int(base64.decodebytes(x.encode()).decode())

@app.route('/get_intersection')
def get_intersection():

    # Request from Query Provider encrypted query
    r = requests.get(f'{QUERY_URL}/get_encrypted_query')
    encoded_encrypted_query = r.json()['encoded_encrypted_query']

    # Send encrypted query to data provider for blinding
    r = requests.post(f'{PROVIDER_URL}/blind_query', json=encoded_encrypted_query)
    encoded_blinded_encrypted_query = r.json()['encoded_blinded_encrypted_query']

    # Send blinded encrypted query to query provider for unblinding
    r = requests.post(f'{QUERY_URL}/unblind_query', json=encoded_blinded_encrypted_query)
    encoded_unblinded_encrypted_query = r.json()['encoded_unblinded_encrypted_query']
    unblinded_encrypted_query = [decode_int(x) for x in encoded_unblinded_encrypted_query]

    # Request from Data Provider encrypted data
    r = requests.get(f'{PROVIDER_URL}/get_provider_data')
    encoded_encrypted_provider_data = r.json()['encoded_encrypted_provider_data']
    encrypted_provider_data = [decode_int(x) for x in encoded_encrypted_provider_data]

    # Find intersection between unblinded encrypted query and encrypted provider data
    intersection = []

    for x in encrypted_provider_data:
        for k, y in enumerate(unblinded_encrypted_query):
            if y == x:
                intersection.append((k))

    return(jsonify({'intersection': intersection}))

if __name__ == '__main__':

    config = json.load(open('./broker_config.json', 'r'))

    QUERY_URL = config['query_url']
    PROVIDER_URL = config['provider_url']

    app.run(host=config['hostname'], port=config['port'])

