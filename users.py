from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from db import db
from datetime import datetime
import requests
import re

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route("/fetch", methods=['GET'])
def fetch_user():
    try:
        page = request.args.get("page")

        if(page == None):
            print(page)
            return "Page is required in query parameter", 400
        
        url = "https://reqres.in/api/users"
        params = {'page': page}
        
        response = requests.get(url=url, params=params)
        data = response.json()

        users = data['data']

        for user in users:
            if(not validate_email(user['email'])):
                continue
            cur = db.connection.cursor()
            cur.execute(
                """SELECT * FROM USERS WHERE id = %s""", (user['id'],)
            )
            userData = cur.fetchone()

            if(userData == None):
                now = datetime.today()
                cur.execute(
                    """INSERT INTO USERS (id, email, first_name, last_name, avatar, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s, %s)""", (user['id'], user['email'], user['first_name'], user['last_name'], user['avatar'], now, now)
                )

        db.connection.commit()
        cur.close()

        return data

    except Exception as e:
        return str(e), 400

@bp.route("/", methods=['GET'])
def get_user():
    try:
        cur = db.connection.cursor()
        cur.execute(
            """SELECT * FROM USERS WHERE deleted_at is null"""

        )
        users = cur.fetchall()
        cur.close()
        
        responseData = []

        for data in users:
            responseData.append({
                'id': data[0],
                'email': data[1],
                'first_name': data[2],
                'last_name': data[3],
                'avatar': data[4],
                'created_at': data[5],
                'updated_at': data[6],
            })

        return responseData

    except Exception as e:
        return str(e), 400

@bp.route("/", methods=['POST'])
def post_user():
    try:
        userData = request.json
        
        if(userData.get("email") == None):
            return "email is required", 400
        
        if(not validate_email(userData['email'])):
            return "email is invalid", 400
        
        now = datetime.today()
        params = [userData['email']]

        if(userData.get("first_name") != None):
            params.append(userData['first_name'])
        else:
            params.append(None)

        if(userData.get("last_name") != None):
            params.append(userData['last_name'])
        else:
            params.append(None)

        if(userData.get("avatar") != None):
            params.append(userData['avatar'])
        else:
            params.append(None)

        params.append(now)
        params.append(now)
        converted = tuple(params)
        
        cur = db.connection.cursor()
        cur.execute(
            """SELECT * FROM USERS WHERE email = %s""", (userData['email'],)
        )
        currentUser = cur.fetchone()

        if(currentUser != None):
            return ("User with email " + userData['email'] + " already exists"), 400

        cur.execute(
            """INSERT INTO USERS(email, first_name, last_name, avatar, created_at, updated_at) VALUES (%s, %s, %s, %s, %s, %s)""", converted
        )
        db.connection.commit()
        cur.close()

        return "User created successfully"
    except Exception as e:
        return str(e), 400

@bp.route("/", methods=['PUT'])
def put_user():
    try:
        userData = request.json
        
        if(userData.get("id") == None):
            return "id is required", 400
        
        cur = db.connection.cursor()
        cur.execute(
            """SELECT * FROM USERS WHERE id=%s""", (userData['id'],)
        )

        currentUser = cur.fetchone()

        if(currentUser == None):
            return "User not found", 400
        
        now = datetime.today()
        params = []

        if(userData.get("email") != None):
            if(not validate_email(userData['email'])):
                return "email is invalid", 400
            params.append(userData['email'])
        else:
            print(currentUser)
            params.append(currentUser[1])

        if(userData.get("first_name") != None):
            params.append(userData['first_name'])
        else:
            params.append(currentUser[2])

        if(userData.get("last_name") != None):
            params.append(userData['last_name'])
        else:
            params.append(currentUser[3])

        if(userData.get("avatar") != None):
            params.append(userData['avatar'])
        else:
            params.append(currentUser[4])

        params.append(now)
        params.append(userData['id'])
        converted = tuple(params)

        print(converted)

        cur.execute(
            """UPDATE USERS SET email=%s, first_name=%s, last_name=%s, avatar=%s, updated_at=%s WHERE id=%s""", converted
        )
        db.connection.commit()
        cur.close()

        return "User updated successfully"
    except Exception as e:
        return str(e), 400

@bp.route("/", methods=['DELETE'])
def del_user():
    try:
        if(request.headers.get('Authorization') == None):
            return "Unauthorized", 401
        
        auth = request.headers['authorization']

        if(auth == "Bearer 3cdcnTiBsl"):
            userData = request.json
        
            if(userData.get("id") == None):
                return "id is required", 400
            
            cur = db.connection.cursor()
            cur.execute(
                """SELECT * FROM USERS WHERE id=%s AND deleted_at IS NULL""", (userData['id'],)
            )

            currentUser = cur.fetchone()

            if(currentUser == None):
                return "User not found", 400
            
            now = datetime.today()
            params = (now, now, userData['id'])

            cur.execute(
                """UPDATE USERS SET updated_at=%s, deleted_at=%s WHERE id=%s""", params
            )
            db.connection.commit()
            cur.close()

            return "User deleted successfully"

        else:
            return "Unauthorized", 401
    except Exception as e:
        print(e)
        return str(e), 400


def validate_email(email):
    if re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return True
    else:
        return False