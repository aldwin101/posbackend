import re
import mariadb
import dbcreds
from flask import request, Response
import json
from app import app
import datetime

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
            cursor.execute("SELECT id, dish_name, price, category, date_created FROM dishes WHERE id=?",[params.get("dishId")])
            dishInfo = cursor.fetchone()
            print(dishInfo)

            if dishInfo:
                if dishInfo != None:
                    dish = {
                        "dishId" : dishInfo[0],
                        "dishName" : dishInfo[1],
                        "price" : dishInfo[2],
                        "category" : dishInfo[3],
                        "dateCreated" : dishInfo[4]
                    }

                    return Response(json.dumps(dish, default=str),
                                    mimetype="application/json",
                                    status=200)
                else:
                    return Response("Invalid id",
                                    mimetype="text/html",
                                    status=200)
            else:
                cursor.execute("SELECT id, dish_name, price, category, date_created FROM dishes")
                allDishes = cursor.fetchall()
                print(allDishes)

                if allDishes != None:
                    dishList = []
                    for dish in allDishes:
                        dishData = {
                            "dishId" : dish[0],
                            "dishName" : dish[1],
                            "price" : dish[2],
                            "category" : dish[3],
                            "dateCreated" : dish[4]
                        }
                        dishList.append(dishData)

                    return Response(json.dumps(dishList,default=str),
                                    mimetype="application/json",
                                    status=200)
        
        # POST method
        elif request.method == "POST":
            data = request.json
            dateCreated = datetime.datetime.today() # get the present date and time
            cursor.execute("SELECT position FROM users INNER JOIN user_login ON users.id=user_login.user_id WHERE login_token=?",[data.get("loginToken")])
            position = cursor.fetchone()[0]
            print(position)

            if position != None:
                if position == "manager":
                    cursor.execute("INSERT INTO dishes(dish_name, price, category, date_created) VALUES(?,?,?,?)",[data.get("dishName"), data.get("price"), data.get("category"), dateCreated])
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
                        "category" : getDish[3],
                        "dateCreated" : getDish[4]
                    }

                    return Response(json.dumps(newDish, default=str),
                                    mimetype="application/json",
                                    status=200)
                else: 
                    return Response("You are not authorized",
                                    mimetype="text/html",
                                    status=400)
            else:
                return Response("Invalid data sent",
                                mimetype="text/html",
                                status=500)

        # PATCH method
        elif request.method == "PATCH":
            data = request.json
            dateModified = datetime.datetime.today()
            cursor.execute("SELECT position FROM users INNER JOIN user_login ON users.id=user_login.user_id WHERE login_token=?",[data.get("loginToken")])
            position = cursor.fetchone()[0]
            print(position)

            cursor.execute("SELECT id FROM dishes WHERE id=?",[data.get("dishId")])
            dishId = cursor.fetchone()[0]
            print(dishId)

            if position != None:
                if position == "manager":
                    if data.get("dishName") != None and data.get("dishName") != "":
                        cursor.execute("UPDATE dishes SET dish_name=?, date_modified=? WHERE id=?", [data.get("dishName"), dateModified, dishId])
                    
                    elif data.get("price") != None and data.get("price") == "":
                        cursor.execute("UPDATE dishes SET price=?, date_modified=? WHERE id=?", [data.get("price"), dateModified, dishId])

                    elif data.get("category") != None and data.get("category") == "":
                        cursor.execute("UPDATE dishes SET category=?, date_modified=? WHERE id=?", [data.get("category"), dateModified, dishId])
                    
                    else: 
                        return Response("Field cannot be empty", 
                                        mimetype="text/html", 
                                        status=400)
                    conn.commit()

                    cursor.execute("SELECT id, dish_name, price, category, date_modified FROM dishes ORDER BY date_modified DESC")
                    getUpdatedDish = cursor.fetchone()
                    print(getUpdatedDish)

                    updatedDish = {
                        "dishId" : getUpdatedDish[0],
                        "dishName" : getUpdatedDish[1],
                        "price" : getUpdatedDish[2],
                        "category" : getUpdatedDish[3],
                        "dateModified" : getUpdatedDish[4]
                    }
                    
                    return Response(json.dumps(updatedDish, default=str),
                                    mimetype="application/json",
                                    status=200)

                else:
                    return Response("You are not authorized!",
                                    mimetype="text/html",
                                    status=400)
            
            else:
                return Response("Invalid data sent",
                                mimetype="text/html",
                                status=400)
                    
        # DELETE method
        elif request.method == "DELETE":
            data = request.json
            cursor.execute("SELECT position FROM users INNER JOIN user_login ON users.id=user_login.user_id WHERE login_token=?",[data.get("loginToken")])
            position = cursor.fetchone()[0]
            print(position)

            cursor.execute("SELECT id FROM dishes WHERE id=?",[data.get("dishId")])
            dishId = cursor.fetchone()[0]
            print(dishId)

            if position != None:
                if position == "manager":
                    cursor.execute("DELETE FROM dishes WHERE id=?", [dishId])
                    conn.commit()

                    return Response("Deleted successfully",
                                    mimetype="text/html",
                                    status=200)
                else: 
                    return Response("You are not authorized",
                                    mimetype="text/html",
                                    status=400)
            else:
                return Response("Invalid data sent",
                                mimetype="text/html",
                                status=500)
        else: 
            return Response("Method not allowed",
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