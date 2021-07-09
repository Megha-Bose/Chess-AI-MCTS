import json
import random
from flask import Flask, render_template, jsonify, request
from chess import *
from mcts import *
# from mcts1 import *

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')
    

@app.route('/best_mcts_move', methods=['POST'])
def best_mcts_move():
    json_post = request.get_json(force=True)
    if ("board" in json_post):
        board = json_post['board']
        chess_board = chess.Board(board)
        num_iter = json_post['iterations']
        best_move = run_mcts(board, num_iter)

        # best move - parent action of best child
        print('best move = '+str(best_move))

        chess_board.push(best_move)

        print(chess_board)

    return jsonify({'board': str(chess_board.fen())})


if __name__ == '__main__':
    app.run(debug=True)
