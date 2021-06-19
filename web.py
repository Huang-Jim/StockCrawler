import logging.config

import json
from bottle import route, run, request, post, static_file
import yaml

from application.general_utils.utils import create_dir
from web_function import run_all

# define logger
yaml_path = "./config.yml"
create_dir('./log')
with open(yaml_path, 'r', encoding='utf-8') as f:
    config = yaml.load(f)
    logging.config.dictConfig(config)
logger = logging.getLogger()
static_dir = './static'

create_dir('./plot')


@post('/search')
def search():
    body = json.load(request.body)
    stock_id = body['stock_id']
    select_item = body['select_item']
    int_item_list = body['int_item_list']
    if_error = run_all(stock_id=int(stock_id),
                       select_item=select_item,
                       int_item_list=int_item_list)
    return if_error


@route('/static/:filename')
def server_abc(filename):
    return static_file(filename, root=static_dir)


@route('/')
def server_static():
    return static_file('index.html', root=static_dir)


run(host='localhost', port=9999, debug=True)
