from flask import Flask
from flask_cors import CORS
import pymysql as sql
import os
#import jwt

#print("JWT_SECRET_KEY", os.environ.get("JWT_SECRET_KEY"))
#Generate the token
'''jwt_secret_key=os.environ.get('JWT_SECRET_KEY')
if not isinstance(jwt_secret_key, str):
    raise TypeError("JWT secret key should be a string.")

payload={"user_email":'abc1@gmail.com'}
token = jwt.encode(payload, jwt_secret_key, algorithm='HS256')
#print(f"Generated Token: {token}")

#decode the token
try:
    decode_payload = jwt.decode(token, jwt_secret_key, algorithms=['HS256'])
    #print(f"Decoded Payload: {decode_payload}")
except jwt.ExpiredSignatureError:
    print("Token has expired.")
except jwt.InvalidTokenError as e:
    print("Invalid token.", str(e))
'''
api = Flask(__name__)
CORS(api)

api.config['MYSQL_HOST'] = 'autorack.proxy.rlwy.net'
api.config['MYSQL_USER'] = 'root'
api.config['MYSQL_PASSWORD'] = 'lLEwJdWOHCQjHqZmKhHmvBPacCNOVRoC'
api.config['MYSQL_DB'] = 'railway'
api.config['MYSQL_PORT'] = 53142

try:
    db = sql.connect(
        host=api.config['MYSQL_HOST'],
        user=api.config['MYSQL_USER'],
        password=api.config['MYSQL_PASSWORD'],
        database=api.config['MYSQL_DB']
    )
    #print("Database connection successful!")
except sql.MySQLError as e:
    print("Error connecting to database:", e)
