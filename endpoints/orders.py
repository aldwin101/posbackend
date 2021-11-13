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
            cursor.execute("SELECT table_number, user_id, dish_name, price, order_date FROM order_content INNER JOIN dishes ON dishes.id=order_content.dish_id INNER JOIN orders ON orders.id=order_content.order_id WHERE order_id=?", [params.get("orderId")])
            getOrders = cursor.fetchall()
            print(getOrders)

            if getOrders:
                if getOrders != None:
                    orders = []
                    for order in getOrders:
                        orderData = {
                            "tableNumber" : order[0],
                            "userId" : order[1],
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
                cursor.execute("SELECT table_number, user_id, dish_name, price, order_date FROM order_content INNER JOIN dishes ON dishes.id=order_content.dish_id INNER JOIN orders ON orders.id=order_content.order_id ORDER BY order_date DESC")
                getOrders = cursor.fetchall()
                print(getOrders)

                if getOrders:
                    if getOrders != None:
                        orders = []
                        for order in getOrders:
                            orderData = {
                                "tableNumber" : order[0],
                                "userId" : order[1],
                                "dishName" : order[2],
                                "price" : order[3],
                                "orderDate" : order[4]
                            }
                            orders.append(orderData)

                        return Response(json.dumps(orders, default=str),
                                        mimetype="application/json",
                                        status=200)

        # POST method
        elif request.method == "POST":
            data = request.json
            isActive = 1
            tableNumber = data.get("tableNumber")
            orderDate = datetime.datetime.today()
            cursor.execute("SELECT user_id FROM user_login WHERE login_token=?", [data.get("loginToken")])
            userId = cursor.fetchone()[0]

            cursor.execute("SELECT id FROM dishes WHERE dish_name=?",[data.get("dishName")])
            dishId = cursor.fetchone()[0]
            
            if userId != None and dishId != None:
                cursor.execute("INSERT INTO orders(order_date, user_id, table_number, is_active) VALUES(?,?,?,?)", [orderDate, userId, tableNumber, isActive])
                conn.commit()
                orderId = cursor.lastrowid
                
                cursor.execute("INSERT INTO order_content(dish_id, order_id) VALUES(?,?)", [dishId, orderId])
                conn.commit()
                
                cursor.execute("SELECT table_number, user_id, dish_name, price, order_date FROM order_content INNER JOIN dishes ON dishes.id=order_content.dish_id INNER JOIN orders ON orders.id=order_content.order_id WHERE table_number=? and user_id=? and is_active=?",[tableNumber, userId, isActive])
                updatedOrder = cursor.fetchone()
                print(updatedOrder)
                
                orders = {
                    "tableNumber": updatedOrder[0],
                    "userId": updatedOrder[1],
                    "dishname": updatedOrder[2],
                    "price": updatedOrder[3],
                    "order_date": updatedOrder[4]
                }
                
                return Response(json.dumps(orders, default=str),
                                mimetype="application/json",
                                status=200)
            
            else:
                return Response("user id or dish id not found",
                                mimetype="text/html",
                                status=400)
        
        # DELETE method
        elif request.method == "DELETE":
            data = request.json
            isActive = 1
            tableNumber = data.get("tableNumber")
            cursor.execute("SELECT user_id FROM user_login WHERE login_token=?", [data.get("loginToken")])
            userId = cursor.fetchone()[0]

            cursor.execute("SELECT id FROM dishes WHERE dish_name=?",[data.get("dishName")])
            dishId = cursor.fetchone()[0]
                
                



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