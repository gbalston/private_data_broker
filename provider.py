from flask import Flask, jsonify, request
import json
import requests
import gmpy2
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import base64
import hashlib

app = Flask(__name__)

def rsa_enc(c):
    return gmpy2.powmod(c, d, n)

def hash_str(x):
    return int(hashlib.sha3_256(x.encode()).hexdigest(), 16)

def hash_int(x):
    return int(hashlib.sha3_256(str(x).encode()).hexdigest(), 16)

def encode_int(x):
    return base64.b64encode(str(x).encode()).decode()

def decode_int(x):
    return int(base64.decodebytes(x.encode()).decode())

@app.route('/get_provider_data')
def get_provider_data():

    return jsonify({
        'encoded_encrypted_provider_data': encoded_provider_data
    })

@app.route('/blind_query', methods=['POST'])
def blind_query():

    encoded_encrypted_query = request.get_json()

    encrypted_query = [decode_int(x) for x in encoded_encrypted_query]
    blinded_encrypted_query = [int(rsa_enc(x)) for x in encrypted_query]

    encoded_blinded_encrypted_query = [encode_int(x) for x in blinded_encrypted_query]

    return jsonify({
        'encoded_blinded_encrypted_query': encoded_blinded_encrypted_query,
    })

if __name__ == '__main__':

    config = json.load(open('./provider_config.json', 'r'))
    BROKER_URL = config['broker_url']

    with open(config['public_key_fp'], 'rb') as key_file:
        pubkey = serialization.load_pem_public_key(key_file.read(), backend=default_backend())

    with open(config['private_key_fp'], 'rb') as key_file:
        prikey = serialization.load_pem_private_key(key_file.read(), password=config['password'].encode(),
                                                    backend=default_backend())

    d = prikey.private_numbers().d
    n = pubkey.public_numbers().n
    e = pubkey.public_numbers().e

    with open(config['provider_data_fp'], 'r') as f:
        provider_data = f.read().split('\n')

    hashed_provider_data = [hash_str(x) for x in provider_data]
    encrypted_provider_data = [hash_int(rsa_enc(x)) for x in hashed_provider_data]
    encoded_provider_data = [encode_int(x) for x in encrypted_provider_data]

    app.run(host=config['hostname'], port=config['port'])

