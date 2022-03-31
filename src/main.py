"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Task
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/todos', methods=['GET', 'POST'])
def handle_todos():
    if request.method == "GET":
        all_todos = Task.query.all()
        all_todos = list(map(lambda task: task.serialize(), all_todos))
        response_body = jsonify(all_todos)
        return response_body
    if request.method == "POST":
        req = request.json
        task = Task(label=f"{req['label']}", done=False)
        db.session.add(task)
        db.session.commit()
        all_todos = Task.query.all()
        all_todos = list(map(lambda task: task.serialize(), all_todos))
        return jsonify(all_todos)
    return None


@app.route('/todo/<int:id>', methods=['DELETE'])
def delete_todo(id):
    task = Task.query.get(id)
    db.session.delete(task)
    db.session.commit()
    all_todos = Task.query.all()
    all_todos = list(map(lambda task: task.serialize(), all_todos))
    return jsonify(all_todos)


@app.route('/todo/<int:task_id>', methods=['PUT'])
def update_todo(task_id):
    task = Task.query.get(task_id)
    req = request.json
    if "label" in req:
        task.label = req["label"]
    if "done" in req:
        task.done = req["done"]
    db.session.commit()
    all_todos = Task.query.all()
    all_todos = list(map(lambda task: task.serialize(), all_todos))
    return jsonify(all_todos)


@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
