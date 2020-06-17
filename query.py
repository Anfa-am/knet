from deeppavlov import build_model

import requests

from googlesearch import search 

import textract
import wikipedia
import random
import json
import time

from goose3 import Goose

from cleantext import clean

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS, cross_origin

extractor = Goose({'enable_image_fetching': False})

knowledgeModel = build_model('./knowledge-cofig.json', download=False)

knowledge = ['']


def reset_knowledge():
    knowledge = ['']
    return

def register_context(query):
    try:
        page = wikipedia.page(query)
    except wikipedia.DisambiguationError as e:
        try:
            page = wikipedia.page(e.options[0])
        except wikipedia.DisambiguationError as e:
            page = wikipedia.page(e.options[0])

    cleaned = clean(page.content, no_urls=True,no_line_breaks=True) 
    extend_knowledge(cleaned)
    return page

def extend_context_url(url):
    article = extractor.extract(url=url)
    if(article.cleaned_text):
        cleaned = clean(article.cleaned_text, no_urls=True,no_line_breaks=True) 

        print(cleaned)
        extend_knowledge(cleaned)
    return 


def extend_context_doc(doc):
    text = textract.process('./' + doc).decode('utf-8')
    cleaned = clean(text, no_urls=True,no_line_breaks=True) 
    extend_knowledge(cleaned)


def extend_knowledge(info):
    knowledge[0] = knowledge[0] + ' ' + info
    # knowledge.append(info)
    return

def learn2(query, depth):
    k = search(query+'-youtube -wikipedia', num=depth, stop=depth, pause=2)
    for j in k:
        print(j)
        extend_context_url(j)
    return 

def learn(query, depth):
    url = 'http://newsapi.org/v2/everything'
    params = {
        'q': query,
        'sortBy': 'relevancy',
        'sources': 'bbc-news,bloomberg,cnn,espn,politico,time',
        'apiKey': '3cd524d2a3a841888f3e512172a567d7'
    }

    r = requests.get(url = url, params = params)
    data = r.json()

    for i in range(0,depth):
        if i < len(data["articles"]):
            extend_context_url(data["articles"][i]["url"])

def answer(question):
    a = knowledgeModel(knowledge, [question])
    return a

app = Flask(__name__)
cors = CORS(app)

@app.route('/', methods=['POST'])
@cross_origin(allow_headers=['Content-Type'])
def setup_context():
    data = json.loads(request.data)
    query = data.get("query")

    reset_knowledge()

    relatives = wikipedia.search(query)
    register_context(relatives[0])

    summary = wikipedia.summary(query, sentences=1)

    res = make_response(jsonify({ "summary": summary }), 200)
    return res

@app.route('/ask', methods=['POST'])
@cross_origin(allow_headers=['Content-Type'])
def thisone():
    data = json.loads(request.data)
    q = data.get("question")
    res = make_response(jsonify({ "question": q, "answer": answer(q) }), 200)
    return res

@app.route('/upload', methods=['POST'])
@cross_origin(allow_headers=['Content-Type'])
def anotherone():
    f = request.files['file']
    f.save(f.filename)
    extend_context_doc(f.filename)

    res = make_response(jsonify({"extended": True}), 200)
    return res

@app.route('/recreate', methods=['POST'])
@cross_origin(allow_headers=['Content-Type'])
def thatone():
    data = json.loads(request.data)
    query = data.get("query")

    layers = data.get("layers")
    depth = data.get("depth")
    
    reset_knowledge()

    relatives = wikipedia.search(query)
    
    if layers > 0:
        for i in range(0, layers):
            if i < len(relatives):
                print(relatives[i])

                register_context(relatives[i])

                # learn(relatives[i], depth)

                learn2(relatives[i], depth)
    else:
        register_context(query)

    res = make_response(jsonify({"recreated":True, "docs": (layers + ((layers * depth) * 2)) }), 200)
    return res

