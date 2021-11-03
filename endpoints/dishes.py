import mariadb
import dbcreds
from flask import request, Response
import json
from app import app

@app.route("/api/dishes", methods = ["GET", "POST", "PATCH", "DELETE"])

def dishes():
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
            cursor.execute("SELECT * FROM dishes WHERE id=?",[params.get("dishId")])
            dishInfo = cursor.fetchone()
            print(dishInfo)

            if dishInfo:
                if dishInfo != None:
                    dish = {
                        "dishId" : dishInfo[0],
                        "dishName" : dishInfo[1],
                        "price" : dishInfo[2],
                        "category" : dishInfo[3]
                    }

                    return Response(json.dumps(dish, default=str),
                                    mimetype="application/json",
                                    status=200)
                else:
                    return Response("Invalid id",
                                    mimetype="text/html",
                                    status=200)
            else:
                cursor.execute("SELECT * FROM dishes")
                allDishes = cursor.fetchall()
                print(allDishes)

                if allDishes != None:
                    dishList = []
                    for dish in allDishes:
                        dishData = {
                            "dishId" : dish[0],
                            "dishName" : dish[1],
                            "price" : dish[2],
                            "category" : dish[3]
                        }
                        dishList.append(dishData)

                    return Response(json.dumps(dishList,default=str),
                                    mimetype="application/json",
                                    status=200)
        
        # POST method
        elif request.method == "POST":
            data = request.json
            cursor.execute("INSERT INTO dishes(dish_name, price, category) VALUES(?,?,?)",[data.get("dishName"), data.get("price"), data.get("category")])
            conn.commit()
            newDishId = cursor.lastrowid
            print(newDishId)

            cursor.execute("SELECT * FROM dishes WHERE id=?",[newDishId])
            getDish = cursor.fetchone()
            print(getDish)

            newDish = {
                "dishId" : getDish[0],
                "dishName" : getDish[1],
                "price" : getDish[2],
                "category" : getDish[3]
            }

            return Response(json.dumps(newDish, default=str),
                            mimetype="application/json",
                            status=200)



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