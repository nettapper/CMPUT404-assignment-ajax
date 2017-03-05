#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle, Conner Dunn
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# You can start this by executing it in python:
# python server.py
#
# remember to:
#     pip install flask


import flask
from flask import Flask, request, Response
import json
app = Flask(__name__)
app.debug = True

# Accessed on Mar 2, 2017
# Written by atupal (http://stackoverflow.com/users/2226698/atupal) on Stack Overflow http://stackoverflow.com/questions/20646822/how-to-serve-static-files-in-flask#20648053
# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='')
# End of code by atupal

# An example world
# {
#    'a':{'x':1, 'y':2},
#    'b':{'x':2, 'y':3}
# }
# curl -v -H "Content-Type: application/json" -X POST http://127.0.0.1:5000/world -d '{ "a":{"x":1, "y":2}, "b":{"x":2, "y":3} }'

class World:
    def __init__(self):
        self.clear()

    def update(self, entity, key, value):
        entry = self.space.get(entity,dict())
        entry[key] = value
        self.space[entity] = entry

    def set(self, entity, data):
        self.space[entity] = data

    def clear(self):
        self.space = dict()

    def get(self, entity):
        return self.space.get(entity,dict())

    def world(self):
        return self.space

# you can test your webservice from the commandline
# curl -v   -H "Content-Type: application/json" -X PUT http://127.0.0.1:5000/entity/X -d '{"x":1,"y":1}'

myWorld = World()

# I give this to you, this is how you get the raw body/data portion of a post in flask
# this should come with flask but whatever, it's not my project.
def flask_post_json():
    # TODO more testing w/ this parsing function
    # print "request.json", request.json
    # print "request.data", request.data
    # print "request.form", request.form
    # print "request.form.keys()", request.form.keys()
    '''Ah the joys of frameworks! They do so much work for you
       that they get in the way of sane operation!'''
    if (request.json != None):
        return request.json
    elif (request.data != None and request.data != ''):
        return json.loads(request.data)
    elif (request.form != None and len(request.form.keys()) > 0):
        return json.loads(request.form.keys()[0])
    else:
        return dict({})

@app.route("/")
def hello():
    '''Return something coherent here.. perhaps redirect to /static/index.html '''
    # Accessed on Mar 2, 2017
    # Written by atupal (http://stackoverflow.com/users/2226698/atupal) on Stack Overflow http://stackoverflow.com/questions/20646822/how-to-serve-static-files-in-flask#20648053
    return app.send_static_file('index.html')
    # End of code by atupal

@app.route("/entity/<entity>", methods=['POST','PUT'])
def update(entity):
    '''update the entities via this interface'''
    if request.method == "PUT" or request.method == "POST":
        worldDict = dict({})
        worldDict[entity] = flask_post_json()
        if tryToUpdateAll(worldDict):
            return get_entity(entity)
        else:
            return Response(status=400)
    else:
        response = Response(status=400)
    return response
    return None

@app.route("/entity/<entity>")
def get_entity(entity):
    '''This is the GET version of the entity interface, return a representation of the entity'''
    entityJsonString = str(json.dumps(myWorld.get(entity)))
    print entityJsonString
    response = Response(response=entityJsonString, mimetype="application/json")
    return response

@app.route("/world", methods=['POST','GET'])
def world():
    '''you should probably return the world here'''
    # print("Method", request.method)
    if request.method == "GET":
        response = get_world_response()
    elif request.method == "POST":
        response = post_world_response()
    else:
        response = Response(status=400)
    return response

def get_world_response():
    # print((myWorld.world()))
    myWorldJsonString = str(json.dumps(myWorld.world()))
    response = Response(response=myWorldJsonString, mimetype="application/json", status=200)
    # print(response)
    return response

def post_world_response():
    if tryToUpdateAll(flask_post_json()):
        return get_world_response()
    else:
        return Response(status=400)

# Takes a dict like: { "a":{"x":1, "y":2}, "b":{"x":2, "y":3} }
def tryToUpdateAll(entityKeyDict):
    if type(entityKeyDict) != type(dict({})):
        return False
    else:
        for entity in entityKeyDict.keys():
            if type(entityKeyDict[entity]) != type(dict({})):
                return False
            else:
                for key in entityKeyDict[entity].keys():
                    # print entity, key, entityKeyDict[entity][key]
                    myWorld.update(entity, key, entityKeyDict[entity][key])
        return True

@app.route("/clear", methods=['POST','GET'])
def clear():
    '''Clear the world out!'''
    if request.method == "GET":
        response = get_clear_world_response()
    elif request.method == "POST":
        response = post_clear_world_response()
    else:
        response = Response(status=400)
    return response

def get_clear_world_response():
    myWorld.clear()
    return get_world_response()

def post_clear_world_response():
    myWorld.clear()
    return post_world_response()

if __name__ == "__main__":
    app.run()
