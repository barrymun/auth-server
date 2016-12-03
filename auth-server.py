import base64
import datetime

from flask import Flask
from flask import request
from flask import jsonify
from flask_pymongo import PyMongo
from Crypto.Cipher import AES

application = Flask(__name__)

mongo = PyMongo(application)

CLIENT_SERVER_KEY = "d41d8cd98f00b204e9800998ecf8427e"
AUTH_SERVER_STORAGE_SERVER_KEY = "d41d8cd98f00b204e9800998ecf8427e"

# Client Authentication
@application.route('/client/create', methods=['GET'])
def client_create():
    db = mongo.db.dist
    db.clients.drop()
    result = db.clients.insert_one(
        {"client_id": "1"
            , "session_key": "928F767EADE2DBFD62BFCD65B8E21"
            , "session_key_expires": (datetime.datetime.utcnow() +
                                      datetime.timedelta(seconds=60 * 60 * 4)).strftime('%Y-%m-%d %H:%M:%S')
            , "public_key": "0123456789abcdef0123456789abcdef"
            , "password": "0dP1jO2zS7111111"}
    )
    return jsonify({})

@application.route('/client/auth', methods=['POST'])
def client_auth():
    data = request.get_json(force=True)
    client_id = data.get('client_id')
    encrypted_password = data.get('encrypted_password')
    print(encrypted_password)
    client = Authentication.auth(client_id, encrypted_password)
    if client:
        return jsonify({'success':True,
                        'session_key':client['session_key'],
                        'session_key_expires':client['session_key_expires']}
        )
    else:
        return jsonify({'success':False})

# File storage servers
class Server:

    def __init__(self):
        pass

    @staticmethod
    def get_servers():
        return mongo.db.dist.servers.find()

    @staticmethod
    def create(host, port):
        db = mongo.db.dist
        result = db.servers.insert_one({"host":host, })


class Authentication:
    def __init__(self):
        pass

    @staticmethod
    def get_client(client_identifier):
        for item in mongo.db.dist.clients.find():
            print item

        return mongo.db.dist.clients.find_one({'client_id': client_identifier})

    @staticmethod
    def encode(key, password):
        cipher = AES.new(key, AES.MODE_ECB)  # never use ECB in strong systems obviously
        encoded = base64.b64encode(cipher.encrypt(password))
        return encoded

    @staticmethod
    def decode(key, encoded):
        cipher = AES.new(key, AES.MODE_ECB)  # never use ECB in strong systems obviously
        decoded = cipher.decrypt(base64.b64decode(encoded))
        return decoded.strip()

    @staticmethod
    def update_client(client_id, data):
        return mongo.db.dist.clients.update({'client_id':client_id}, data, upsert=True)


    @staticmethod
    def auth(client_id, encrypted_password):
        client = Authentication.get_client(client_id)
        client_public_key = client['public_key']
        decoded_password = Authentication.decode(client_public_key, encrypted_password)
        if decoded_password == client['password']:
            session_key = md5.new().hexdigest()
            session_key_expires = (datetime.datetime.utcnow() +
                                   datetime.timedelta(seconds=60*250)).strftime('%Y-%m-%d %H:%M:%S')
            client['session_key'] = session_key
            client['session_key_expires'] = session_key_expires
            if Authentication.update_client(client_id, client):
                return client
            else:
                return False
        else:
            return False


if __name__ == '__main__':
    application.run()