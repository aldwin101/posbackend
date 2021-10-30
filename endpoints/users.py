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
            cursor.execute("SELECT id, username, firstname, lastname, position, pin, mobile_phone, home_phone, created FROM users WHERE id=?", [params.get("userId")])
            userData = cursor.fetchone()
            print(userData)
            password = "defpass"
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(16))
            print(hashed)
            dateCreated = datetime.date.today()
            print(dateCreated)
            userPin = random.randint(10000,99999)
            print(userPin)

            
            if userData:
                if userData != None:
                    user = {
                        "userId" : userData[0],
                        "username" : userData[1],
                        "firstName" : userData[2],
                        "lastName" : userData[3],
                        "position" : userData[4],
                        "pin" : userData[5],
                        "mobilePhone" : userData[6],
                        "homePhone" : userData[7],
                        "created" : userData[8]
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
                cursor.execute("SELECT id, username, firstname, lastname, position, pin, mobile_phone, home_phone, created FROM users")
                allUsersData = cursor.fetchall()
                print(allUsersData)

                if allUsersData != None:
                    usersList = []
                    for users in allUsersData:
                        userData = {
                            "userId" : users[0],
                            "username" : users[1],
                            "firstName" : users[2],
                            "lastName" : users[3],
                            "position" : users[4],
                            "pin" : users[5],
                            "mobilePhone" : users[6],
                            "homePhone" : users[7],
                            "created" : users[8]
                        }
                        usersList.append(userData)
                    
                    return Response(json.dumps(usersList, default=str),
                                    mimetype="application/json",
                                    status=200)
        
        # POST method
        # Create a user
        elif request.method == "POST":
            data = request.json
            password = "defpass" # assign default password
            userPin = random.randint(10000,99999) # generate 5 digit pin
            dateCreated = datetime.date.today() # date today
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt(14)) # hashed and salted password
            
            # Create new user
            cursor.execute("INSERT INTO users (username, firstname, lastname, password, pin, position, mobile_phone, home_phone, created) VALUES (?,?,?,?,?,?,?,?,?) ",
                [data.get("username"), data.get("firstName"), data.get("lastName"), hashed, userPin, data.get("position"), data.get("mobilePhone"), data.get("homePhone"), dateCreated])
            conn.commit()
            newUserId = cursor.lastrowid
            
            print(newUserId)

            cursor.execute("SELECT id, username, firstname, lastname, pin, position, mobile_phone, home_phone, created FROM users WHERE id=?", [newUserId])
            newUserData = cursor.fetchone()

            newUser = {
                "userId" : newUserData[0],
                "username" : newUserData[1],
                "firstName" : newUserData[2],
                "lastName" : newUserData[3],
                "pin" : newUserData[4],
                "position" : newUserData[5],
                "mobilePhone" : newUserData[6],
                "homePhone" : newUserData[7],
                "created" : newUserData[8]
            }

            return Response(json.dumps(newUser, default=str),
                            mimetype="application/json",
                            status=200)

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