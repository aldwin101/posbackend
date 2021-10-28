import mariadb
import dbcreds
from flask import request, Response
import json
from app import app

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
            cursor.execute("SELECT id, firstname, lastname, position, pin, mobile_phone, home_phone FROM users WHERE id=?", [params.get("userId")])
            userData = cursor.fetchone()
            print(userData)

            if userData:
                if userData != None:
                    user = {
                        "userId" : userData[0],
                        "firstName" : userData[1],
                        "lastName" : userData[2],
                        "position" : userData[3],
                        "pin" : userData[4],
                        "mobilePhone" : userData[5],
                        "homePhone" : userData[6]
                    }

                    return Response(json.dumps(user),
                                    mimetype="application/json",
                                    status=200)
            
                else:
                    return Response(json.dumps("Invalid user id"),
                                    mimetype="application/json",
                                    status=404)
            else:
                # Get all users and return all users information.
                cursor.execute("SELECT id, firstname, lastname, position, pin, mobile_phone, home_phone FROM users")
                usersData = cursor.fetchall()
                print(usersData)

                usersList = []

                for users in usersData:
                    user = {
                        "userId" : users[0],
                        "firstName" : users[1],
                        "lastName" : users[2],
                        "position" : users[3],
                        "pin" : users[4],
                        "mobilePhone" : users[5],
                        "homePhone" : users[6]
                    }
                    usersList.append(user)
                
                return Response(json.dumps(usersList),
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