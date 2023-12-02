import os, http_codes, jwt, bcrypt, env
from flask import Flask, jsonify, request
from lib.model.DBWrapper import DBWrapper
from datetime import datetime, timedelta
from authentication import Authentication

app = Flask(__name__)

TEMPLATES_AUTO_RELOAD = True

app.config['JSON_AS_ASCII'] = False

# -*- coding: utf-8 -*-

# !!! START !!!
@app.route("/")
def hello_world():

    return jsonify({"message": "Bem vindo à API do Food Saver"}), http_codes.OK

# !!! LOGIN !!!
@app.patch("/api/users/")
def login():

    parameters = request.get_json()

    received_parameters = ['email', 'password']

    if not all(parameter in parameters for parameter in received_parameters):

        return jsonify({'message': 'Pedido mal formado'}), http_codes.BAD_REQUEST

    procedure = '''user_login'''

    db_wrapper = DBWrapper()
    db_wrapper.connect()

    data = db_wrapper.query(procedure, [parameters["email"]], 'one')

    db_wrapper.close()

    if data and len(data) > 0:

        print(1)

        token = jwt.encode({
                    'id': data["id"],
                    'expiration': str(datetime.utcnow() + timedelta(weeks=5))
                }, os.getenv("TOKEN_SECRET_KEY"))

        return jsonify({'token': str(token)}), http_codes.OK
    
    elif data is not None and len(data) == 0 or not bcrypt.checkpw(parameters["password"].encode('utf8'), data["password"]):

        return jsonify({'message': 'Credênciais inválidas'}), http_codes.NOT_FOUND

    else:

        return jsonify({'message': 'Erro no servidor'}), http_codes.INTERNAL_SERVER_ERROR


# !!! USERS !!!
@app.post("/api/users/")
def insert_user():

    parameters = request.get_json()

    received_parameters = ['name', 'email', 'password', 'phone_number']

    if not all(parameter in parameters for parameter in received_parameters):

        return jsonify({'message': 'Pedido mal formado'}), http_codes.BAD_REQUEST

    procedure = '''insert_user'''

    db_wrapper = DBWrapper()
    db_wrapper.connect()

    parameters["password"] = bcrypt.hashpw(parameters["password"].encode('utf8'), bcrypt.gensalt(12))

    inserted = db_wrapper.manipulate(procedure, [parameters["name"], parameters["email"], parameters["password"], parameters["phone_number"]])

    db_wrapper.close()

    if inserted:

        return jsonify({'message': 'Inserido com sucesso'}), http_codes.OK

    else:

        return jsonify({'message': 'Não inserido'}), http_codes.INTERNAL_SERVER_ERROR

# !!! ENTITIES !!!
@app.get("/api/entities/")
@app.get("/api/entities/<id>/")
@Authentication
def entities(entity_id = None):

    return http_codes.OK

# !!! ENTITIES WITH OFFERS !!!
@app.get("/api/entities/withoffers/")
@Authentication
def entities_withoffers():

    return http_codes.OK

# !!! OFFERS OF THE ENTITIES !!!
@app.get("/api/entities/offers/")
@app.get("/api/entities/offers/<id>/")
@Authentication
def entities_offers(offer_id = None):

    return http_codes.OK

# !!! BUY OFFER !!!
@app.post("/api/entities/offers/buy/")
@Authentication
def buy_offers():

    return http_codes.OK

# !!! PURCHASES !!!
@app.get("/api/users/purchases/")
@app.patch("/api/users/purchases/")
@Authentication
def purchases():

    return http_codes.OK


if __name__ == "__main__":
    app.run(debug=True)

