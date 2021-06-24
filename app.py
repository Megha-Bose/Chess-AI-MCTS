import json, random
from flask import Flask, render_template, jsonify, request
from chess import *
from mcts import *
# from mcts1 import *
from game import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# @app.route('/new_game')
# def new_game():
#     board = Chess()
#     return jsonify({'board': str(board.fen())})

@app.route('/best_mcts_move', methods = ['POST'])
def best_mcts_move():
    json_post = request.get_json(force = True)
    if ("board" in json_post):
        board = json_post['board']
        num_iter = json_post['iterations']
        best_move = run_mcts(board, num_iter)
        board.move(best_move)

    return jsonify({'board': str(board.get_fen())})

if __name__ == '__main__':
    app.run(debug=True)