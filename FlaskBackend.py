
#Imports
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_restx import Api, Resource, fields
from marshmallow import Schema, fields as parse_fields, ValidationError
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix
import json
import os

#API and App creation
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)
api = Api(app, version='1.1', title='Working Backend API', description='Work on a Python API to be used for later projects')
app.config["JSONIFY_PRETTYPRINT_REGULAR"] = True
CORS(app)

#Namespace
ns = api.namespace('items', description='Backend items')

#Data model
data_model = api.model('Data',
    {'name': fields.String,
      'id': fields.Integer
    })

#QuerySchema
class item_query(Schema):
    name = parse_fields.String (required=False)
    id = parse_fields.Integer (required=False)

querySchema = item_query()

#Load data from JSON
def load_data():
    with open('data.json', 'r') as dataFile:
        return json.load(dataFile)
    
#Save data to JSON
def save_data(data_input):
    with open('data.json', 'w') as dataFile:
        json.dump(data_input, dataFile)

#Main API route - querying and parameters
@ns.route('/data')
class Query(Resource):

    #GET method - Uses name and id paramehers; marshal list with data_model; uses querySchema
    @ns.doc(params = {
        'name': 'Name of the user',
        'id': 'ID of the user'
    })
    @api.produces(['application/json'])
    def get(self):

        try:
            args = querySchema.load(request.args)
   
        except ValidationError as err:
            return {'Errors': err.messages}, 400

        inp_name = args.get('name')
        inp_id = args.get('id')

        elements = load_data()
        all_users = elements['users']

        if (inp_name):
            selected = [elem for elem in all_users if elem['name'].lower() == inp_name.lower()]

        elif (inp_id):
            selected = [elem for elem in all_users if elem['id'] == inp_id]

        try:
            if (selected):
                return selected, 200
        
        except: 
            return {'Errors': "Data with inputed arguments not found"}
    

    #POST method - expects data_model and produces application/json
    @ns.expect(data_model)
    @api.produces(['application/json'])
    def post(self):
        args = api.payload
        currData = load_data()
        currData['users'].append(args)
        save_data(currData)
        return args


#Running the app   
if (__name__=='__main__'):
    app.run()