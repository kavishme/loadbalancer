#!/usr/bin/env python3

from flask import Flask
from flask import request
from flask import Response
from flask_api import status
import model
from model import db
from model import Expense
from model import createDB
#from model import app as application
import simplejson as json
from sqlalchemy.exc import IntegrityError
import os
import redis

# initate flask app
app = Flask(__name__)

#app.SQLALCHEMY_TRACK_MODIFICATION = False

@app.route('/v1/expenses', methods=['POST'])
def expenses():
    try:
        jdata = request.get_json(force=True)
        name = jdata['name']
        email = jdata['email']
        category = jdata['category']
        description = jdata['description']
        link = jdata['link']
        status = 'Pending' #jdata['status']
        estimated_costs = jdata['estimated_costs']
        submit_date = jdata['submit_date']
        decision_date = ' ' #jdata['decision_date']
        expense = Expense(name, email, category, description, link, status, estimated_costs, submit_date, decision_date)
        db.session.add(expense)
        db.session.commit()
        return Response(response = json.dumps({
            "id":expense.id,
            "name":name,
            "email":email,
            "category":category,
            "description":description,
            "link":link,
            "status":status,
            "estimated_costs":estimated_costs,
            "submit_date":submit_date,
            "decision_date":decision_date
        }), status = 201, mimetype='application/json')
    except IntegrityError:
        return Response(status = 400)



@app.route('/v1/expenses/<int:expenseid>', methods = ['GET', 'PUT', 'DELETE'])
def expense(expenseid):
    try:
        expense = Expense.query.filter_by(id=expenseid).first_or_404()
        if request.method == 'GET':
            return Response(response = json.dumps({
                "id":expense.id,
                "name":expense.name,
                "email":expense.email,
                "category":expense.category,
                "description":expense.description,
                "link":expense.link,
                "status":expense.status,
                "estimated_costs":expense.estimated_costs,
                "submit_date":expense.submit_date,
                "decision_date":expense.decision_date
            }), status = 200, mimetype='application/json')
        elif request.method == 'PUT':
            jdata = request.get_json(force = True)
            expense.estimated_costs = jdata['estimated_costs']
            db.session.commit()
            return Response(status = 202)
        else:
            db.session.delete(expense)
            db.session.commit()
            return Response(status = 204)
    except IntegrityError:
        return Response(status=404)

# run app service 
if __name__ == "__main__":

    redis_db = redis.StrictRedis(host="redisserver", port=6379, db=0)
    ports = redis_db.get('routeports')
    if ports:
        ports = ports.decode('utf-8').split(',')
    else:
        ports = []
    if os.environ["LISTENPORT"] not in ports:
        ports.append(os.environ["LISTENPORT"])
    redis_db.set('routeports', ','.join(ports))
#    createDB(model.HOSTNAME)
    app.run(host="0.0.0.0", port=int(os.environ["LISTENPORT"]), debug=True)
    print(os.environ["LISTENPORT"])
    print("over")
    #app.run(host="0.0.0.0", port=5000, debug=True)
