
"""
The chess board is a 2d list
** represents an empty square
"""
chess_board = [
    ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
    ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
    ["**", "**", "**", "**", "**", "**", "**", "**"],
    ["**", "**", "**", "**", "**", "**", "**", "**"],
    ["**", "**", "**", "**", "**", "**", "**", "**"],
    ["**", "**", "**", "**", "**", "**", "**", "**"],
    ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
    ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]

piece_value_pos = {"Q": 9, "R": 5, "B": 3, "N": 3, "p": 1, "K": 0}

bishop_values = [[0.2, 0.1, 0.2, 0.3, 0.3, 0.2, 0.1, 0.2],
                 [0.1, 0.5, 0.4, 0.5, 0.5, 0.4, 0.5, 0.1],
                 [0.2, 0.4, 0.5, 0.6, 0.6, 0.5, 0.4, 0.2],
                 [0.2, 0.5, 0.5, 0.6, 0.6, 0.5, 0.5, 0.2],
                 [0.2, 0.4, 0.6, 0.6, 0.6, 0.6, 0.4, 0.2],
                 [0.2, 0.4, 0.6, 0.6, 0.6, 0.6, 0.4, 0.2],
                 [0.1, 0.5, 0.4, 0.5, 0.5, 0.4, 0.5, 0.1],
                 [0.2, 0.1, 0.2, 0.3, 0.3, 0.2, 0.1, 0.2]]

pawn_values = [[0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9, 0.9],
               [0.7, 0.7, 0.75, 0.8, 0.8, 0.75, 0.7, 0.7],
               [0.4, 0.4, 0.5, 0.6, 0.6, 0.5, 0.4, 0.4],
               [0.2, 0.3, 0.3, 0.5, 0.5, 0.3, 0.3, 0.2],
               [0.1, 0.2, 0.2, 0.4, 0.4, 0.2, 0.2, 0.1],
               [0.1, 0.1, 0.1, 0.2, 0.2, 0.1, 0.1, 0.1],
               [0.2, 0.3, 0.3, 0.0, 0.0, 0.3, 0.3, 0.2],
               [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]]

knight_values = [[0.0, 0.05, 0.1, 0.2, 0.2, 0.1, 0.05, 0.0],
                 [0.0, 0.2, 0.4, 0.5, 0.5, 0.4, 0.2, 0.0],
                 [0.1, 0.5, 0.6, 0.6, 0.6, 0.6, 0.5, 0.1],
                 [0.2, 0.5, 0.7, 0.8, 0.8, 0.7, 0.5, 0.2],
                 [0.2, 0.5, 0.7, 0.8, 0.8, 0.7, 0.5, 0.2],
                 [0.1, 0.5, 0.6, 0.6, 0.6, 0.6, 0.5, 0.1],
                 [0.0, 0.2, 0.4, 0.5, 0.5, 0.4, 0.2, 0.0],
                 [0.0, 0.05, 0.1, 0.2, 0.2, 0.1, 0.05, 0.0]]

queen_values = [[0.1, 0.0, 0.1, 0.3, 0.3, 0.1, 0.0, 0.1],
                [0.1, 0.2, 0.3, 0.4, 0.4, 0.3, 0.2, 0.1],
                [0.2, 0.3, 0.4, 0.5, 0.5, 0.4, 0.3, 0.2],
                [0.2, 0.4, 0.5, 0.7, 0.6, 0.5, 0.4, 0.2],
                [0.2, 0.4, 0.5, 0.6, 0.7, 0.5, 0.4, 0.2],
                [0.2, 0.3, 0.4, 0.5, 0.5, 0.4, 0.3, 0.2],
                [0.1, 0.2, 0.3, 0.4, 0.4, 0.3, 0.2, 0.1],
                [0.1, 0.0, 0.1, 0.3, 0.3, 0.1, 0.0, 0.1]]


rook_values = [[0.2, 0.3, 0.3, 0.6, 0.6, 0.3, 0.3, 0.2],
               [0.4, 0.5, 0.7, 0.8, 0.8, 0.7, 0.5, 0.4],
               [0.0, 0.3, 0.3, 0.6, 0.6, 0.3, 0.3, 0.0],
               [0.0, 0.3, 0.3, 0.5, 0.5, 0.3, 0.3, 0.0],
               [0.0, 0.3, 0.3, 0.4, 0.4, 0.3, 0.3, 0.0],
               [0.0, 0.3, 0.3, 0.4, 0.4, 0.3, 0.3, 0.0],
               [0.0, 0.3, 0.3, 0.4, 0.4, 0.3, 0.3, 0.0],
               [0.2, 0.3, 0.5, 0.6, 0.6, 0.5, 0.3, 0.2]]





class Move:
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_square, end_square, board, is_enpassant=False, is_castle_move=False):
        self.is_castle_move = is_castle_move
        self.is_enpassant = is_enpassant

        self.start_row = start_square[0]
        self.end_row = end_square[0]
        self.start_col = start_square[1]
        self.end_col = end_square[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.is_pawn_promotion = (self.piece_moved == "wp" and self.end_row == 0) or (
                self.piece_moved == "bp" and self.end_row == 7)
        if self.is_enpassant:
            self.piece_captured = "wp" if self.piece_moved == "bp" else "bp"

        self.is_capture = self.piece_captured != "**"
        self.moveID = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    def get_rank_file(self, row, col):
        return self.cols_to_files[col] + self.rows_to_ranks[row]


    #over write
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def __str__(self):
        if self.is_castle_move:
            return "0-0" if self.end_col == 6 else "0-0-0"

        end_square = self.get_rank_file(self.end_row, self.end_col)

        if self.piece_moved[1] == "p":
            if self.is_capture:
                return self.cols_to_files[self.start_col] + "x" + end_square
            else:
                return end_square + "Q" if self.is_pawn_promotion else end_square

        move_string = self.piece_moved[1]
        if self.is_capture:
            move_string += "x"
        return move_string + end_square


    def get_chess_notation(self):
        if self.is_pawn_promotion:
            return self.get_rank_file(self.end_row, self.end_col) + "Q"
        if self.is_castle_move:
            if self.end_col == 1:
                return "0-0-0"
            else:
                return "0-0"
        if self.is_enpassant:
            return self.get_rank_file(self.start_row, self.start_col)[0] + "x" + self.get_rank_file(self.end_row,
                                                                                                self.end_col) + " e.p."
        if self.piece_captured != "**":
            if self.piece_moved[1] == "p":
                return self.get_rank_file(self.start_row, self.start_col)[0] + "x" + self.get_rank_file(self.end_row,
                                                                                                    self.end_col)
            else:
                return self.piece_moved[1] + "x" + self.get_rank_file(self.end_row, self.end_col)
        else:
            if self.piece_moved[1] == "p":
                return self.get_rank_file(self.end_row, self.end_col)
            else:
                return self.piece_moved[1] + self.get_rank_file(self.end_row, self.end_col)





class CastleRights:
    def __init__(self, wk, bk, wq, bq):
        self.wk = wk
        self.wq = wq
        self.bk = bk
        self.bq = bq


