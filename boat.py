from flask import Blueprint, request, make_response, render_template_string
from google.cloud import datastore
import json
import constants

#used class lectures, previous assignment, https://stackoverflow.com/questions/49390075/how-do-i-convert-python-json-into-a-html-table-in-flask-server/49391508, https://stackoverflow.com/questions/49253142/check-response-headers-value-in-postman-tests

client = datastore.Client()

bp = Blueprint('boat', __name__, url_prefix='/boats')

@bp.route('/', methods=['POST'])
def boats_get_post():
    if request.method == 'POST':
        content = request.get_json()
        if 'name' not in content.keys():
            return({'Error': "need a name"}, 400)
        if 'type' not in content.keys():
            return({'Error': "need a type"}, 400)
        if 'length' not in content.keys():
            return({'Error': "need a length"}, 400)
        query = client.query(kind=constants.boats)
        allBoats = query.fetch()
        for x in allBoats:
            if x['name'] == content['name']:
                return({'Error': "A boat with that name already exists"}, 403)
        new_boat = datastore.entity.Entity(key=client.key(constants.boats))
        new_boat.update({'name': content['name'], 'type': content['type'],
          'length': content['length']})
        client.put(new_boat)
        boat = client.get(key=new_boat.key)
        if boat is None:
            return ({'Error': 'Error creating'}, 204)
        boat['id'] = new_boat.key.id
        boat['self'] = request.host_url + '/boats/' + str(new_boat.key.id)
        return (boat, 201)
    else:
        return ('Method not recogonized', 405)

@bp.route('/<id>', methods=['DELETE', 'GET', 'PUT', 'PATCH'])
def boats_put_delete_get(id):
    if request.method == 'DELETE':
        boat_key = client.key(constants.boats, int(id))
        boat = client.get(key=boat_key)
        if boat is None:
            return({'Error': 'No boat with this ID exists'}, 404)
        else:
            client.delete(boat_key)
            return ('', 204)
    elif request.method == 'GET':
        boat_key = client.key(constants.boats, int(id))
        boat = client.get(key=boat_key)
        if boat is None:
            return('Invalid boat ID', 404)
        else:
            boat['id'] = id
            boat['self'] = request.host_url + '/boats/' + str(id)
            if 'text/html' in request.accept_mimetypes:
                htmlBoat = render_template_string('''
                <li>
                    <ul>{{ boat.name }}</ul>
                    <ul>{{ boat.type }}</ul>
                    <ul>{{ boat.length }}</ul>
                </li>
                ''', boat=boat)
                res = make_response(htmlBoat)
                res.headers.set('Content-Type', 'text/html')
                res.status_code = 200
                return res
            elif 'application/json' in request.accept_mimetypes:
                return (boat, 200)
            else:
                return ({'Error': "Content-Type not supported"}, 406)
    elif request.method == 'PUT':
        content = request.get_json()
        if 'name' not in content.keys():
            return({'Error': "need a name"}, 400)
        if 'type' not in content.keys():
            return({'Error': "need a type"}, 400)
        if 'length' not in content.keys():
            return({'Error': "need a length"}, 400)
        query = client.query(kind=constants.boats)
        allBoats = query.fetch()
        for x in allBoats:
            if x['name'] == content['name']:
                return({'Error': "A boat with that name already exists"}, 403)
        boat_key = client.key(constants.boats, int(id))
        boat = client.get(key=boat_key)
        if boat is None:
            return('There is no boat by that ID', 404)
        else:
            boat['name'] = content['name']
            boat['type'] = content['type']
            boat['length'] = content['length']
            client.put(boat)
            boat['self'] = request.host_url + 'boats/' + str(id)
            res = make_response('')
            res.headers.set('Location', boat['self'])
            res.status_code = 303
            return res
    elif request.method == 'PATCH':
        content = request.get_json()
        boat_key = client.key(constants.boats, int(id))
        boat = client.get(key=boat_key)
        if boat is None:
            return('There is no boat by that ID', 404)
        if 'name' in content.keys():
            boat['name'] = content['name']
        if 'type' in content.keys():
            boat['type'] = content['type']
        if 'length' in content.keys():
            boat['length'] = content['length']
        client.put(boat)
        boat['self'] = request.host_url + 'boats/' + str(id)
        return (boat['self'], 200)
    else:
        return ('Method not recogonized', 405)
