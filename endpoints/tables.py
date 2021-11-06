from os import stat
import mariadb
import dbcreds
from flask import request, Response
import json
from app import app

@app.route("/api/tables", methods = ["POST", "DELETE"])

def tables():
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
            

        if request.method == "POST":
            data = request.json
            cursor.execute("SELECT user_id FROM user_login WHERE login_token=?", [data.get("loginToken")])
            userId = cursor.fetchone()[0]
            isActive = 1

            if userId != None:
                cursor.execute("INSERT INTO tables(is_active, user_id) VALUES (?,?)", [isActive, userId])
                conn.commit()

                cursor.execute("SELECT tables.id, user_id, firstname, position FROM users INNER JOIN tables ON users.id=tables.user_id WHERE users.id=?", [userId])
                userInfo = cursor.fetchone()
                print(userInfo)

                user = {
                    "tableId" : userInfo[0],
                    "userId" : userInfo[1],
                    "firstName" : userInfo[2],
                    "position" : userInfo[3]
                }

                return Response(json.dumps(user, default=str),
                                mimetype="application/json",
                                status=200)
            
            else:
                return Response("Token does not exist",
                                mimetype="text/html",
                                status=200)

        elif request.method == "DELETE":
            data = request.json
            cursor.execute("SELECT user_id FROM user_login WHERE login_token=?", [data.get("loginToken")])
            userId = cursor.fetchone()[0]
            print(userId)
            
            cursor.execute("SELECT id FROM tables WHERE id=?", [data.get("tableId")])
            tableId = cursor.fetchone()[0]
            print(tableId)

            if userId != None:
                cursor.execute("DELETE FROM tables WHERE id=?", [tableId])
                conn.commit()

                return Response("Successfully deleted",
                                mimetype="text/html",
                                status=200)

            else:
                return Response("Delete failed",
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
        if (conn != None):
            conn.rollback()
            conn.close()
        else:
            print("The connection never opened, nothing to close here")