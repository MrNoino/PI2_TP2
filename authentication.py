import jwt
from functools import wraps
from flask import jsonify, request
import http_codes
from datetime import datetime
import os, env
from lib.DBWrapper import DBWrapper

def Authentication(func):

    @wraps(func)
    def verify_token(*args, **kwargs):

        if "Authorization" in request.headers:

            token = request.headers["Authorization"]

        else:

            return jsonify({'message': 'Token está em falta!'}), http_codes.BAD_REQUEST

        if not token:

            return jsonify({'message': 'Token está em falta!'}), http_codes.BAD_REQUEST

        try:

            procedure = '''check_token'''

            db_wrapper = DBWrapper()
            db_wrapper.connect()

            exists = db_wrapper.query(procedure, [str(token)], fetch_mode="one")

            db_wrapper.close()

            if not exists["exist"]:

                return jsonify({"message": "Token inativo"}), http_codes.UNAUTHORIZED

            decoded_token = jwt.decode(token, os.getenv("TOKEN_SECRET_KEY"), algorithms=["HS256"])

            if(decoded_token["expiration"] < str(datetime.utcnow())):

                return jsonify({"message": "O Token expirou!"}), http_codes.FORBIDDEN

        except Exception as e:

            return jsonify({'message': str(e)}), http_codes.UNAUTHORIZED
        
        return func(*args, **kwargs)
    
    return verify_token