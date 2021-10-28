import mariadb
import dbcreds
from flask import request, Response
import json
import uuid
from app import app

@app.route("/api/login", methods = ["POST", "DELETE"])

def login():
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
            
            # Allow the user to login provided the correct required data
        if request.method == "POST":
            data = request.json
            cursor.execute("SELECT id FROM users WHERE username=? and password=?", [data.get("username"), data.get("password")])
            userId = cursor.fetchone()[0]
            print(userId)

            if userId != None:
                loginToken = uuid.uuid4().hex
                cursor.execute("INSERT INTO user_login(user_id, login_token) VALUES(?,?)",[userId, loginToken])
                conn.commit()

                cursor.execute("SELECT users.id, firstname, lastname, position, pin, login_token FROM users INNER JOIN user_login ON users.id=user_login.user_id WHERE users.id=?", [userId])
                getUserData = cursor.fetchone()
                print(getUserData)

                userData = {
                    "userId" : getUserData[0],
                    "firstName" : getUserData[1],
                    "lastName" : getUserData[2],
                    "position" : getUserData[3],
                    "pin" : getUserData[4],
                    "loginToken" : getUserData[5],
                }
                
                return Response(json.dumps(userData),
                                mimetype="application/json",
                                status=200)
            else:
                return Response("Invalid pin",
                                mimetype="text/html",
                                status=400)

            # Allow the user to logout provided the correct required data
        elif request.method == "DELETE":
            data = request.json
            cursor.execute("SELECT user_id FROM user_login WHERE login_token=?", [data.get("loginToken")])
            userId = cursor.fetchone()[0]
            print(userId)

            if userId != None:
                cursor.execute("DELETE FROM user_login WHERE user_id=?", [userId])
                conn.commit()

                return Response("Deleted successfully",
                                mimetype="text/html",
                                status=200)
            
            else:
                return Response("Invalid token",
                                mimetype="text/html",
                                status=400)

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
        # Check the connection
        if (conn != None):
            conn.rollback()
            conn.close()
        else:
            print("The connection never opened, nothing to close here")