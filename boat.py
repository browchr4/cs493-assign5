from flask import Blueprint, request, jsonify
from google.cloud import datastore
import json
import constants

client = datastore.Client()

bp = Blueprint('boat', __name__, url_prefix='/boats')

@bp.route('/', methods=['POST','GET'])
def boats_get_post():
    if request.method == 'POST':
        content = request.get_json()
        if 'name' not in content.keys():
            return("need a name", 400)
        if 'type' not in content.keys():
            return("need a type", 400)
        if 'length' not in content.keys():
            return("need a length", 400)
        new_boat = datastore.entity.Entity(key=client.key(constants.boats))
        new_boat.update({'name': content['name'], 'type': content['type'],
          'length': content['length'], 'loads': []})
        client.put(new_boat)
        return str(new_boat.key.id)
    elif request.method == 'GET':
        query = client.query(kind=constants.boats)
        q_limit = int(request.args.get('limit', '3'))
        q_offset = int(request.args.get('offset', '0'))
        l_iterator = query.fetch(limit= q_limit, offset=q_offset)
        pages = l_iterator.pages
        results = list(next(pages))
        if l_iterator.next_page_token:
            next_offset = q_offset + q_limit
            next_url = request.base_url + "?limit=" + str(q_limit) + "&offset=" + str(next_offset)
        else:
            next_url = None
        for e in results:
            selfLink = request.host_url + 'boats/' + str(e.key.id)
            e["self"] = selfLink
        output = {"boats": results}
        if next_url:
            output["next"] = next_url
        return json.dumps(output)
    else:
        return 'Method not recogonized'

@bp.route('/<id>', methods=['DELETE', 'GET'])
def boats_put_delete_get(id):
    if request.method == 'DELETE':
        boat_key = client.key(constants.boats, int(id))
        boat = client.get(key=boat_key)
        if boat is None:
            return('Invalid boat ID', 400)
        elif len(boat['loads']) == 0:
            client.delete(boat_key)
            return ('', 200)
        else:
            for x in boat['loads']:
                load_key = client.key(constants.loads, int(x))
                load = client.get(key=load_key)
                load.update({'owner': load['owner'], 'boat': '', 'weight': load['weight'], 'contents': load['contents']})
                client.put(load)
            client.delete(boat_key)
            return ('', 200)
    elif request.method == 'GET':
        boat_key = client.key(constants.boats, int(id))
        boat = client.get(key=boat_key)
        if boat is None:
            return('Invalid boat ID', 400)
        else:
            output = []
            for x in boat['loads']:
                load_key = client.key(constants.loads, int(x))
                load = client.get(key=load_key)
                load['self'] = request.host_url + '/loads/' + str(x)
                output.append(load)
            boat['loads'] = output
            return (boat, 200)
    else:
        return 'Method not recogonized'

