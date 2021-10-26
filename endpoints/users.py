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
        if request.method == "GET":
            params = request.args.get("userId")
            if params == int:
                cursor.execute("SELECT id, firstname, lastname, position FROM employees WHERE id=?", [params])
                result = isinstance(params.get("userId"), int)
                print (result)
                userData = cursor.fetchone()
                print(userData)

                user = {
                    "userId" : userData[0],
                    "firstName" : userData[1],
                    "lastName" : userData[2],
                    "position" : userData[3]
                }

                return Response(json.dumps(user),
                                mimetype="application/json",
                                status=200)
            
            else:
                cursor.execute("SELECT id, firstname, lastname, position FROM employees")
                employees = cursor.fetchall()
                print(employees)

                if employees != None:
                    allEmployees = []
                    for employee in employees:
                        employeeData = {
                            "userId" : employee[0],
                            "firstName" : employee[1],
                            "lastName" : employee[2],
                            "position" : employee[3]
                        }
                        allEmployees.append(employeeData)

                    return Response(json.dumps(allEmployees),
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
        # Check the connection
        if (conn != None):
            conn.rollback()
            conn.close()
        else:
            print("The connection never opened, nothing to close here")