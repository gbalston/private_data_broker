import secrets
import json
from flask import Flask, jsonify, request
import requests
import gmpy2
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
import base64
import hashlib

app = Flask(__name__)

def blind_message(x, _r):
    return (gmpy2.powmod(_r, e, n) * x) % n

def unblind_message(x, _r):
    return (x * gmpy2.invert(_r, n)) % n

def hash_str(x):
    return int(hashlib.sha3_256(x.encode()).hexdigest(), 16)

def hash_int(x):
    return int(hashlib.sha3_256(str(x).encode()).hexdigest(), 16)

def encode_int(x):
    return base64.b64encode(str(x).encode()).decode()

def decode_int(x):
    return int(base64.decodebytes(x.encode()).decode())

@app.route('/get_encrypted_query')
def get_query_data():
    return jsonify({
        'encoded_encrypted_query': encoded_encrypted_query
    })

@app.route('/unblind_query', methods=['POST'])
def unblind_query():

    encoded_blinded_encrypted_query = request.get_json()

    blinded_encrypted_query = [decode_int(x) for x in encoded_blinded_encrypted_query]
    unblinded_encrypted_query = [hash_int(unblind_message(x, rand_n[i])) for i, x in enumerate(blinded_encrypted_query)]
    encoded_unblinded_encrypted_query = [encode_int(x) for x in unblinded_encrypted_query]
    
    return(jsonify({'encoded_unblinded_encrypted_query': encoded_unblinded_encrypted_query}))

if __name__ == '__main__':

    gen_rand = secrets.SystemRandom()

    config = json.load(open('./query_config.json', 'r'))
    BROKER_URL = config['broker_url']

    with open(config['public_key_fp'], 'rb') as key_file:
        pubkey = serialization.load_pem_public_key(key_file.read(), backend=default_backend())

    n = pubkey.public_numbers().n
    e = pubkey.public_numbers().e

    with open(config['query_data_fp'], 'r') as f:
        query = f.read().split('\n')

    hashed_query = [hash_str(x) for x in query]

    encrypted_query = []
    rand_n = []

    for x in hashed_query:
        r = gen_rand.randrange(n)
        rand_n.append(r)
        encrypted_query.append(int(blind_message(x, r)))

    encoded_encrypted_query = [encode_int(x) for x in encrypted_query]

    app.run(host=config['hostname'], port=config['port'])
