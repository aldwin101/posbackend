import mariadb
import dbcreds
from flask import request, Response
import json
from app import app
import datetime

@app.route("/api/orders", methods = ["GET", "POST", "PATCH", "DELETE"])

def orders():
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
            
        if request.method == "GET":
            params = request.args
            cursor.execute("SELECT orders.id, user_id, dish_name, price, order_date FROM dishes INNER JOIN orders ON dishes.id=orders.dish_id WHERE orders.id=?", [params.get("orderId")])
            orderInfo = cursor.fetchone()

            if orderInfo:
                if orderInfo != None:
                    order = {
                        "orderId" : orderInfo[0],
                        "userId" : orderInfo[1],
                        "dishName" : orderInfo[2],
                        "price" : orderInfo[3],
                        "orderDate" : orderInfo[4]
                    }
                    return Response(json.dumps(order,default=str),
                                    mimetype="application/json",
                                    status=200)
                else:
                    return Response("Invalid id",
                                    mimetype="text/html",
                                    status=400)
            else:
                cursor.execute("SELECT orders.id, user_id, dish_name, price, order_date FROM dishes INNER JOIN orders ON dishes.id=orders.dish_id ORDER BY order_date DESC")
                getOrders = cursor.fetchall()
                print(getOrders)

                if getOrders != None:
                    allOrders = []
                    for orders in getOrders:
                        order = {
                            "orderId" : orders[0],
                            "userId" : orders[1],
                            "dishName" : orders[2],
                            "price" : orders[3],
                            "orderDate" : orders[4]
                        }
                        allOrders.append(order)

                    return Response(json.dumps(allOrders, default=str),
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