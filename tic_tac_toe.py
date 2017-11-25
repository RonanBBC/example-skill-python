import logging
from random import randint, choice
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session

app = Flask(__name__)
ask = Ask(app, "/")
logging.getLogger("flask_ask").setLevel(logging.DEBUG)

with open('positions.txt') as f:
    POSITIONS = [l.strip() for l in list(f)]

@ask.launch
@ask.intent('StartIntent')
def new_game():
    first = randint(0, 1)
    board = [''] * 9

    if first == 1:
        position = randint(0, 8)
        board[position] = 'a'
        welcome_msg = render_template(
            'start_alexa', position=POSITIONS[position])
    else:
        welcome_msg = render_template('start_player')

    session.attributes['board'] = board
    return question(welcome_msg)

@ask.intent('MoveIntent', convert={'position': str})
def move(position):

    def check_board(board):
        lines = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]
        for line in lines:
            if board[line[0]] == board[line[1]] and board[line[0]] == board[line[2]]:
                if board[line[0]] == 'a':
                    return 'a'
                if board[line[0]] == 'p':
                    return 'p'

        try:
            board.index('')
        except ValueError:
            return 't'

    def make_move(board):
        valid_moves = [index for (index, value) in enumerate(board) if value == '']
        return choice(valid_moves)

    position = POSITIONS.index(position)
    
    board = session.attributes['board']
    if board[position]:
        return question(render_template('invalid_move'))
    board[position] = 'p'

    result = check_board(board)
    if result == 'p':
        return statement(render_template('player_win'))
    if result == 't':
        return statement(render_template('tie'))

    position = make_move(board)
    board[position] = 'a'

    result = check_board(board)
    if result == 'a':
        return statement(render_template('alexa_win', position=POSITIONS[position]))
    if result == 't':
        return statement(render_template('alexa_tie', position=POSITIONS[position]))

    return question(render_template('alexa_move', position=POSITIONS[position]))

if __name__ == '__main__':
    app.run(debug=True)
