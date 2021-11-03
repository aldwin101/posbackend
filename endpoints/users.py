import mariadb
import dbcreds
from flask import request, Response
import json
from app import app
import random
import datetime
import bcrypt


#users endpoint
@app.route("/api/users", methods = ["GET", "POST", "PATCH", "DELETE"])

# users handler
def users():
    try:
        cursor = None
        conn = None

        conn = mariadb.connect(
                        user=dbcreds.user,
                        password=dbcreds.password,
                        host=dbcreds.host,
                        port=dbcreds.port,
                        database=dbcreds.database
                        )
        cursor = conn.cursor()
        
        # GET method
        # Get a specific user or get all the users.
        if request.method == "GET":
            # Get a specific user using userId as params and return user information.
            params = request.args
            cursor.execute("SELECT id, username, firstname, lastname, position, mobile_phone, home_phone, created FROM users WHERE id=?", [params.get("userId")])
            userData = cursor.fetchone()
            
            if userData:
                if userData != None:
                    user = {
                        "userId" : userData[0],
                        "username" : userData[1],
                        "firstName" : userData[2],
                        "lastName" : userData[3],
                        "position" : userData[4],
                        "mobilePhone" : userData[5],
                        "homePhone" : userData[6],
                        "created" : userData[7]
                    }

                    return Response(json.dumps(user, default=str),
                                    mimetype="application/json",
                                    status=200)
            
                else:
                    return Response("Invalid user id",
                                    mimetype="application/json",
                                    status=404)
            else:
                # Get all users and return all users information.
                cursor.execute("SELECT id, username, firstname, lastname, position, mobile_phone, home_phone, created FROM users")
                allUsersData = cursor.fetchall()

                if allUsersData != None:
                    usersList = []
                    for users in allUsersData:
                        userData = {
                            "userId" : users[0],
                            "username" : users[1],
                            "firstName" : users[2],
                            "lastName" : users[3],
                            "position" : users[4],
                            "mobilePhone" : users[5],
                            "homePhone" : users[6],
                            "created" : users[7]
                        }
                        usersList.append(userData)
                    
                    return Response(json.dumps(usersList, default=str),
                                    mimetype="application/json",
                                    status=200)
        
        # POST method
        elif request.method == "POST":
            data = request.json
            password = "defpass"
            userPin = random.randint(10000,99999)
            dateCreated = datetime.date.today()
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(14))
            
            # Allow the user to create new user
            cursor.execute("INSERT INTO users (username, firstname, lastname, password, position, pin, mobile_phone, home_phone, created) VALUES (?,?,?,?,?,?,?,?,?) ",
                [data.get("username"), data.get("firstName"), data.get("lastName"), hashed, data.get("position"), userPin, data.get("mobilePhone"), data.get("homePhone"), dateCreated])
            conn.commit()
            newUserId = cursor.lastrowid
            
            cursor.execute("SELECT id, username, firstname, lastname, position, pin, mobile_phone, home_phone, created FROM users WHERE id=?", [newUserId])
            newUserData = cursor.fetchone()

            newUser = {
                "userId" : newUserData[0],
                "username" : newUserData[1],
                "firstName" : newUserData[2],
                "lastName" : newUserData[3],
                "position" : newUserData[4],
                "pin" : newUserData[5],
                "mobilePhone" : newUserData[6],
                "homePhone" : newUserData[7],
                "created" : newUserData[8]
            }

            return Response(json.dumps(newUser, default=str),
                            mimetype="application/json",
                            status=200)

        # PATCH method
        elif request.method == "PATCH":
            data = request.json
            cursor.execute("SELECT user_id FROM user_login WHERE login_token=?", [data.get("loginToken")])
            userId = cursor.fetchone()[0]

            # Allow the user to edit the information individually
            if userId != None:
                if data.get("username") != None and data.get("username") != "":
                    cursor.execute("UPDATE users SET username = ? WHERE id=?", [data.get("username"), userId])

                elif data.get("firstname") != None and data.get("firstname") != "":
                    cursor.execute("UPDATE users SET firstname = ? WHERE id=?", [data.get("firstname"), userId])

                elif data.get("lastname") != None and data.get("lastname") != "":
                    cursor.execute("UPDATE users SET lastname = ? WHERE id=?", [data.get("lastname"), userId])
                
                elif data.get("password") != None and data.get("password") != "":
                    cursor.execute("UPDATE users SET password = ? WHERE id=?", [data.get("password"), userId])
                
                elif data.get("pin") != None and data.get("pin") != "":
                    cursor.execute("UPDATE users SET pin = ? WHERE id=?", [data.get("pin"), userId])

                elif data.get("mobile_phone") != None and data.get("mobile_phone") != "":
                    cursor.execute("UPDATE users SET mobile_phone = ? WHERE id=?", [data.get("mobile_phone"), userId])

                elif data.get("home_phone") != None and data.get("") != "":
                    cursor.execute("UPDATE users SET home_phone = ? WHERE id=?", [data.get("home_phone"), userId])

                else: 
                    return Response("Field cannot be empty", 
                                    mimetype="text/html", 
                                    status=400)
                conn.commit()

                cursor.execute("SELECT * FROM users WHERE id=?", [userId])
                getUpdatedData = cursor.fetchone()

                updatedData = {
                    "userId" : getUpdatedData[0],
                    "username" : getUpdatedData[1],
                    "firstName" : getUpdatedData[2],
                    "lastName" : getUpdatedData[3],
                    "mobilePhone" : getUpdatedData[5],
                    "homePhone" : getUpdatedData[6]
                }

                return Response(json.dumps(updatedData),
                            mimetype="application/json",
                            status=200)
            else:
                return Response("Invalid user id",
                            mimetype="text/html",
                            status=404)

        # DELETE method
        elif request.method == "DELETE":
            data = request.json
            password = data.get("password")
            cursor.execute("SELECT password, login_token FROM users INNER JOIN user_login ON users.id=user_login.user_id WHERE login_token=?", [data.get("loginToken")])
            reqData = cursor.fetchone()
            pwFromDB = reqData[0]
            loginToken = reqData[1]

            if (bcrypt.checkpw(password.encode(), pwFromDB.encode())): # compare pw provided by the user and pw from the db
                cursor.execute("DELETE users, user_login FROM users INNER JOIN user_login ON users.id=user_login.user_id WHERE login_token=?",[loginToken])
                conn.commit()

                return Response("Deleted suucessfully",
                                mimetype="text/html",
                                status=200)
            else:
                return Response("Wrong data provided",
                                mimetype="text/html",
                                status=404)

        else:
            return Response("Request not allowed",
                            mimetype="text/html",
                            status=500)


    except mariadb.OperationalError:
        print("Operational error on the query")
    except mariadb.DataError:
        print("Something wrong with your data")
    except mariadb.OperationalError:
        print("Something wrong with the connection")
    except mariadb.ProgrammingError:
        print("Your query was wrong")
    except mariadb.IntegrityError:
        print("Your query would have broken the database and we stopped it")
    except:
        print("Something went wrong")
    finally:
        if (cursor != None):
            cursor.close()
        else:
            print("There was never a cursor to begin with")
        if (conn != None):
            conn.rollback()
            conn.close()
        else:
            print("The connection never opened, nothing to close here")