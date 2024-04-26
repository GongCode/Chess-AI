import random
import ChessLib

CHECKMATE = 10000
STALEMATE = 0
DEPTH = 3

piece_position_values = {"wB": ChessLib.bishop_values,
                         "bB": ChessLib.bishop_values[::-1],
                         "wN": ChessLib.knight_values,
                         "bN": ChessLib.knight_values[::-1],
                         "wR": ChessLib.rook_values,
                         "bR": ChessLib.rook_values[::-1],
                         "wp": ChessLib.pawn_values,
                         "bp": ChessLib.pawn_values[::-1],
                         "wQ": ChessLib.queen_values,
                         "bQ": ChessLib.queen_values[::-1]
                         }

def find_random_move(valid_moves):
    return random.choice(valid_moves)

def find_best_move(game_state, valid_moves, return_queue):
    global next_move
    next_move = None
    random.shuffle(valid_moves)
    find_move_minmax(game_state, valid_moves, DEPTH, -CHECKMATE, CHECKMATE,
                             1 if game_state.white_move else -1)
    return_queue.put(next_move)

def find_move_minmax(game_state, valid_moves, depth, alpha, beta, turn_multiplier):
    global next_move
    if depth == 0:
        return turn_multiplier * score_chess_board(game_state)
    max_score = -CHECKMATE
    for move in valid_moves:
        game_state.make_move(move)
        next_moves = game_state.get_valid_moves()
        score = -find_move_minmax(game_state, next_moves, depth - 1, -beta, -alpha, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        game_state.undo_move()
        if max_score > alpha:
            alpha = max_score
        if alpha >= beta:
            break
    return max_score


def score_chess_board(game_state):
    if game_state.checkmate:
        if game_state.white_move:
            return -CHECKMATE  
        else:
            return CHECKMATE 
    elif game_state.stalemate:
        return STALEMATE
    score = 0
    for row in range(len(game_state.board)):
        for col in range(len(game_state.board[row])):
            piece = game_state.board[row][col]
            if piece != "**":
                piece_position_score = 0
                if piece[1] != "K":
                    piece_position_score = piece_position_values[piece][row][col]
                if piece[0] == "w":
                    score += ChessLib.piece_value_pos[piece[1]] + piece_position_score
                if piece[0] == "b":
                    score -= ChessLib.piece_value_pos[piece[1]] + piece_position_score

    return score





