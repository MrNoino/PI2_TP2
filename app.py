import os, http_codes, jwt, bcrypt
from flask import Flask, jsonify, request
from lib.DBWrapper import DBWrapper
from datetime import datetime, date, timedelta
from authentication import Authentication

app = Flask(__name__)

app.config['JSON_AS_ASCII'] = False

# !!! START !!!
@app.route("/")
def welcome():

    return jsonify({"message": "Bem vindo à API do Food Saver"}), http_codes.OK

# !!! USERS !!!
@app.post("/api/users/")
def insert_user():

    parameters = request.get_json()

    received_parameters = ['name', 'email', 'password', 'phone_number']

    if not all(parameter in parameters for parameter in received_parameters):

        return jsonify({'message': 'Pedido mal formado'}), http_codes.BAD_REQUEST
    
    db_wrapper = DBWrapper()
    db_wrapper.connect()

    procedure = "exists_user_email"

    exists_user_email = db_wrapper.query(procedure, [parameters["email"]], fetch_mode= 'one')

    if exists_user_email and exists_user_email['exists'] > 0:

        return jsonify({'message': 'Email já em uso'}), http_codes.CONFLICT

    procedure = '''insert_user'''

    parameters["password"] = bcrypt.hashpw(parameters["password"].encode('utf8'), bcrypt.gensalt(12))

    inserted = db_wrapper.manipulate(procedure, [parameters["name"], parameters["email"], parameters["password"], parameters["phone_number"], 1])

    db_wrapper.close()

    if inserted:

        return jsonify({'message': 'Inserido com sucesso'}), http_codes.OK

    else:

        return jsonify({'message': 'Não inserido'}), http_codes.INTERNAL_SERVER_ERROR

# !!! LOGIN !!!
@app.patch("/api/users/")
def login():

    parameters = request.get_json()

    received_parameters = ['email', 'password']

    if not all(parameter in parameters for parameter in received_parameters):

        return jsonify({'message': 'Pedido mal formado'}), http_codes.BAD_REQUEST
    
    db_wrapper = DBWrapper()
    db_wrapper.connect()

    procedure = '''user_login'''

    user = db_wrapper.query(procedure, [parameters["email"]], fetch_mode= 'one')

    db_wrapper.close()

    if user and bcrypt.checkpw(parameters["password"].encode('utf8'), user["password"].encode('utf8')):

        db_wrapper = DBWrapper()
        db_wrapper.connect()

        procedure = '''is_user_active'''

        is_active = db_wrapper.query(procedure, [user["id"]], fetch_mode= 'one')

        if is_active and not is_active["active"]:

            return jsonify({'message': "Cliente inativo"}), http_codes.UNAUTHORIZED

        token = jwt.encode({
                    'id': user["id"],
                    'expiration': str(datetime.utcnow() + timedelta(weeks=5))
                }, os.getenv("TOKEN_SECRET_KEY"))

        procedure = '''update_token'''

        updated = db_wrapper.manipulate(procedure, [user["id"], token])

        db_wrapper.close()

        if not updated:

            return jsonify({'message': updated}), http_codes.INTERNAL_SERVER_ERROR

        return jsonify({'token': str(token)}), http_codes.OK
    
    elif user is not None or not bcrypt.checkpw(parameters["password"].encode('utf8'), user["password"]):

        return jsonify({'message': 'Credênciais inválidas'}), http_codes.NOT_FOUND

    else:

        return jsonify({'message': 'Erro no servidor'}), http_codes.INTERNAL_SERVER_ERROR

# !!! LOGOUT !!!
@app.patch("/api/users/logout/")
@Authentication
def logout():

    decoded_token = jwt.decode(request.headers["Authorization"], os.getenv("TOKEN_SECRET_KEY"), algorithms=["HS256"])

    procedure = '''update_token'''

    db_wrapper = DBWrapper()
    db_wrapper.connect()

    updated = db_wrapper.manipulate(procedure, [decoded_token["id"], None])

    db_wrapper.close()

    if not updated:

        return jsonify({'message': 'Erro no servidor'}), http_codes.INTERNAL_SERVER_ERROR
    
    return jsonify({'message': 'Sessão terminada com sucesso'}), http_codes.OK

# !!! ENTITIES !!!
@app.get("/api/entities/")
@app.get("/api/entities/<entity_id>/")
@Authentication
def entities(entity_id = None):

    db_wrapper = DBWrapper()
    db_wrapper.connect()

    if entity_id:

        procedure = '''get_entity'''

        data = db_wrapper.query(procedure, [entity_id], fetch_mode= "one")

    else:

        sql = '''SELECT * FROM get_active_entities'''

        data = db_wrapper.query(sql, is_procedure=False)

    db_wrapper.close()

    if data and len(data) > 0:

        return jsonify(data), http_codes.OK
    
    elif data is not None and len(data) == 0:

        return jsonify({'message': 'Nenhuma entidade encontrada'}), http_codes.NOT_FOUND

    else:

        return jsonify({'message': 'Erro no servidor'}), http_codes.INTERNAL_SERVER_ERROR


# !!! ENTITIES WITH OFFERS !!!
@app.get("/api/entities/withoffers/")
@Authentication
def entities_withoffers():

    db_wrapper = DBWrapper()
    db_wrapper.connect()

    sql = '''SELECT * FROM get_active_entities'''

    entities = db_wrapper.query(sql, is_procedure=False, fetch_mode= "all")


    if entities is None:

        return jsonify({'message': 'Erro no servidor'}), http_codes.INTERNAL_SERVER_ERROR


    procedure = '''get_today_offers_by_entity'''

    for key, entity in enumerate(entities):

        offers = db_wrapper.query(procedure, [entity["id"]], fetch_mode= "all")

        if not offers:

            entities.pop(key)

        else:

            entities[key]["offers"] = offers

    db_wrapper.close()

    if not entities:

        return jsonify({'message': 'Nenhuma entidade com ofertas encontrada'}), http_codes.NOT_FOUND

    return jsonify(entities), http_codes.OK

# !!! OFFERS OF THE ENTITIES !!!
@app.get("/api/entities/offers/")
@app.get("/api/entities/offers/<entity_id>/")
@Authentication
def entities_offers(entity_id = None):

    db_wrapper = DBWrapper()
    db_wrapper.connect()

    if entity_id:

        procedure = '''get_today_offers_by_entity'''

        data = db_wrapper.query(procedure, [entity_id], fetch_mode= "all")

    else:

        sql = '''SELECT * FROM get_today_offers'''

        data = db_wrapper.query(sql, is_procedure=False, fetch_mode= "all")

        if data is None:

            return jsonify({'message': 'Erro no servidor'}), http_codes.INTERNAL_SERVER_ERROR

        procedure = '''get_entity'''

        for key, offer in enumerate(data):

            entity = db_wrapper.query(procedure, [offer["entity_id"]], fetch_mode= "one")

            data[key]["entity"] = entity
    
    db_wrapper.close()

    if data and len(data) > 0:

        return jsonify(data), http_codes.OK
    
    elif data is not None and len(data) == 0:

        return jsonify({'message': 'Nenhuma oferta encontrada'}), http_codes.NOT_FOUND

    else:

        return jsonify({'message': 'Erro no servidor'}), http_codes.INTERNAL_SERVER_ERROR

# !!! BUY OFFER !!!
@app.post("/api/entities/offers/buy/")
@Authentication
def buy_offer():

    decoded_token = jwt.decode(request.headers["Authorization"], os.getenv("TOKEN_SECRET_KEY"), algorithms=["HS256"])

    db_wrapper = DBWrapper()
    db_wrapper.connect()

    procedure = '''is_user_active'''

    is_active = db_wrapper.query(procedure, [decoded_token["id"]], fetch_mode= 'one')

    if is_active and not is_active["active"]:

        return jsonify({'message': "Cliente inativo"}), http_codes.UNAUTHORIZED

    parameters = request.get_json()

    received_parameters = ['offer_id']

    if not all(parameter in parameters for parameter in received_parameters):

        return jsonify({'message': 'Pedido mal formado'}), http_codes.BAD_REQUEST

    procedure = '''is_offer_available'''

    is_offer_available = db_wrapper.query(procedure, [parameters["offer_id"]], fetch_mode= 'one')

    if is_offer_available and not is_offer_available["available"]:

        return jsonify({'message': "Oferta indisponível"}), http_codes.UNAUTHORIZED

    procedure = '''buy_offer'''

    bought = db_wrapper.manipulate(procedure, [parameters["offer_id"], decoded_token["id"], 1, 0, 1])

    db_wrapper.close()

    if bought:

        return jsonify({'message': "Oferta adquirida com sucesso"}), http_codes.OK

    else:

        return jsonify({'message': 'Oferta não adquirida'}), http_codes.INTERNAL_SERVER_ERROR

# !!! PURCHASES !!!
@app.route("/api/users/purchases/", methods=['GET', 'PATCH'])
@Authentication
def purchases():

    db_wrapper = DBWrapper()
    db_wrapper.connect()

    decoded_token = jwt.decode(request.headers["Authorization"], os.getenv("TOKEN_SECRET_KEY"), algorithms=["HS256"])

    if request.method == 'GET':

        procedure = '''get_purchases'''

        pur = db_wrapper.query(procedure, [decoded_token["id"]], fetch_mode= 'all')

        if pur:

            procedure1 = '''get_offer'''
            procedure2 = '''get_entity'''

            for index, purchase in enumerate(pur):
                
                offer = db_wrapper.query(procedure1, [purchase["offer_id"]], fetch_mode= 'one')
                pur[index]['offer'] = offer
                pur[index]['entity'] = db_wrapper.query(procedure2, [offer["entity_id"]], fetch_mode= 'one')

            db_wrapper.close()

            return jsonify(pur), http_codes.OK
        
        elif pur is not None:

            db_wrapper.close()

            return jsonify({'message': 'Nenhuma compra encontrada'}), http_codes.NOT_FOUND

        else:

            db_wrapper.close()

            return jsonify({'message': 'Erro no servidor'}), http_codes.INTERNAL_SERVER_ERROR


    else:
            
        parameters = request.get_json()

        received_parameters = ['offer_id']

        if not all(parameter in parameters for parameter in received_parameters):

            return jsonify({'message': 'Pedido mal formado'}), http_codes.BAD_REQUEST
        
        procedure = '''get_purchase'''

        purchase = db_wrapper.query(procedure, [parameters['offer_id'], decoded_token["id"]], decoded_token["id"], fetch_mode= 'one')

        if purchase is not None:

            if not purchase:

                return jsonify({'message': 'Compra não encontrada'}), http_codes.NOT_FOUND

        else: 

            return jsonify({'message': 'Erro no servidor'}), http_codes.INTERNAL_SERVER_ERROR

        procedure = '''get_offer'''

        offer = db_wrapper.query(procedure, [parameters['offer_id']], fetch_mode= 'one')

        if offer is not None:

            if not offer:

                return jsonify({'message': 'Oferta não encontrada'}), http_codes.NOT_FOUND

        else: 

            return jsonify({'message': 'Erro no servidor'}), http_codes.INTERNAL_SERVER_ERROR

        if offer['date'] != date.today():
            
            return jsonify({'message': 'Data da oferta expirada'}), http_codes.FORBIDDEN
        
        procedure = '''cancel_purchase'''
        
        inserted = db_wrapper.manipulate(procedure, [parameters['offer_id'], decoded_token["id"]])

        if inserted:

            return jsonify({'message': 'Compra cancelada com sucesso'}), http_codes.OK
        
        else:

            return jsonify({'message': 'Compra não cancelada'}), http_codes.INTERNAL_SERVER_ERROR


if __name__ == "__main__":
    app.run(debug=True)