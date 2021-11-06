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

        # POST method
        elif request.method == "POST":
            data = request.json
            orderDate = datetime.datetime.today()
            cursor.execute("SELECT user_id FROM user_login WHERE login_token=?", [data.get("loginToken")])
            userId = cursor.fetchone()[0]
            print(userId)

            cursor.execute("SELECT id FROM dishes WHERE dish_name=?",[data.get("dishName")])
            dishId = cursor.fetchone()[0]
            print(dishId)

            cursor.execute("SELECT id FROM tables WHERE id=?", [data.get("tableId")])
            tableId = cursor.fetchone()[0]
            print(tableId)


            if userId != None and dishId != None:
                cursor.execute("INSERT INTO orders(order_date, user_id) VALUES(?,?)", [orderDate, userId])
                conn.commit()
                orderId = cursor.lastrowid

                cursor.execute("INSERT INTO table_orders(order_id, table_id) VALUES(?,?)", [orderId, tableId])
                conn.commit()

                cursor.execute("INSERT INTO order_content(dish_id, order_id) VALUES(?,?)", [dishId, orderId])
                conn.commit()
            












                # cursor.execute("SELECT tables.id, user_id, dish_id, price, order_date FROM tables INNER JOIN orders ON orders.id=tables.order_id INNER JOIN order_content ON orders.id=order_content.order_id INNER JOIN dishes ON dishes.id=order_content.dish_id WHERE tables.id=?", [tableId])
                # newOrder = cursor.fetchone()
                # print(newOrder)



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