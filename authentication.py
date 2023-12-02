import jwt
from functools import wraps
from flask import jsonify, request
import http_codes
from datetime import datetime
import os, env

def Authentication(func):

    @wraps(func)
    def verify_token(*args, **kwargs):

        if "Authorization" in request.headers:

            token = request.headers["Authorization"].split(" ")[1]

        else:

            return jsonify({'Erro': 'Token está em falta!'}), http_codes.BAD_REQUEST

        if not token:

            return jsonify({'Erro': 'Token está em falta!'}), http_codes.BAD_REQUEST

        try:

            decoded_token = jwt.decode(token, os.environ["SECRET_KEY"], algorithms=["HS256"])

            if(decoded_token["expiration"] < str(datetime.utcnow())):

                return jsonify({"Erro": "O Token expirou!"}), http_codes.FORBIDDEN

        except Exception as e:

            return jsonify({'Erro': str(e)}), http_codes.UNAUTHORIZED
        
        return func(*args, **kwargs)
    
    return verify_token