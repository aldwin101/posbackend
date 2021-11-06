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
        
        # GET method
        if request.method == "GET":
            params = request.args
            cursor.execute("SELECT user_id, dish_id, dish_name, price, order_date FROM order_content INNER JOIN dishes ON dishes.id=order_content.dish_id INNER JOIN orders ON orders.id=order_content.order_id WHERE order_id=?", [params.get("orderId")])
            getOrders = cursor.fetchall()
            print(getOrders)

            if getOrders:
                if getOrders != None:
                    orders = []
                    for order in getOrders:
                        orderData = {
                            "userId" : order[0],
                            "dishId" : order[1],
                            "dishName" : order[2],
                            "price" : order[3],
                            "orderDate" : order[4]
                        }
                        orders.append(orderData)

                    return Response(json.dumps(orders, default=str),
                                    mimetype="application/json",
                                    status=200)
                
                else:
                    return Response("Invalid id",
                                    mimetype="text/html",
                                    status=404)
            
            else:
                cursor.execute("SELECT user_id, dish_id, dish_name, price, order_date FROM order_content INNER JOIN dishes ON dishes.id=order_content.dish_id INNER JOIN orders ON orders.id=order_content.order_id ORDER BY order_date DESC")
                getOrders = cursor.fetchall()
                print(getOrders)

                if getOrders:
                    if getOrders != None:
                        orders = []
                        for order in getOrders:
                            orderData = {
                                "userId" : order[0],
                                "dishId" : order[1],
                                "dishName" : order[2],
                                "price" : order[3],
                                "orderDate" : order[4]
                            }
                            orders.append(orderData)

                        return Response(json.dumps(orders, default=str),
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