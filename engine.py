"""
Storing information about the current state of the game
Determines valid moves.
"""
from ChessLib import Move, chess_board, CastleRights
import copy

class GameState:
    def __init__(self):
        # The chess board is a 2d list
        # ** represents an empty square
        self.board = copy.deepcopy(chess_board)
        self.move_methods = {"p": self.get_pawn_moves, "R": self.get_rook_moves, "N": self.get_knight_moves,
                              "B": self.get_bishop_moves, "Q": self.get_queen_moves, "K": self.get_king_moves}

        self.white_king_loc = (7, 4)
        self.black_king_loc = (0, 4)
        self.checkmate = False
        self.stalemate = False
        self.is_in_check = False
        self.white_move = True
        self.can_enpassant = ()
        self.enpassant_log = [self.can_enpassant]
        self.move_log = []
        self.curr_castling_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(self.curr_castling_rights.wk, self.curr_castling_rights.bk,
                                               self.curr_castling_rights.wq, self.curr_castling_rights.bq)]
        self.pins = []
        self.checks = []


    def get_possible_moves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == "w" and self.white_move) or (turn == "b" and not self.white_move):
                    piece = self.board[row][col][1]
                    self.move_methods[piece](row, col, moves)
        return moves

    def make_move(self, move):
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.board[move.start_row][move.start_col] = "**"
        self.move_log.append(move)
        self.white_move = not self.white_move

        if move.piece_moved == "wK":
            self.white_king_loc = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.black_king_loc = (move.end_row, move.end_col)

        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + "Q"

        if move.is_enpassant:
            self.board[move.start_row][move.end_col] = "**"

        if move.piece_moved[1] == "p" and abs(move.start_row - move.end_row) == 2:
            self.can_enpassant = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.can_enpassant = ()

        # castle
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][
                    move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = '**'
            else:
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][
                    move.end_col - 2]
                self.board[move.end_row][move.end_col - 2] = '**'

        self.enpassant_log.append(self.can_enpassant)

        self.update_castle_rights(move)
        self.castle_rights_log.append(CastleRights(self.curr_castling_rights.wk, self.curr_castling_rights.bk,
                                                   self.curr_castling_rights.wq, self.curr_castling_rights.bq))

    def undo_move(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_move = not self.white_move
            if move.piece_moved == "wK":
                self.white_king_loc = (move.start_row, move.start_col)
            elif move.piece_moved == "bK":
                self.black_king_loc = (move.start_row, move.start_col)
            if move.is_enpassant:
                self.board[move.end_row][move.end_col] = "**"
                self.board[move.start_row][move.end_col] = move.piece_captured

            self.enpassant_log.pop()
            self.can_enpassant = self.enpassant_log[-1]

            self.castle_rights_log.pop()
            self.curr_castling_rights = self.castle_rights_log[
                -1]
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col - 1] = '**'
                else:
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = '**'
            self.checkmate = False
            self.stalemate = False

    def get_valid_moves(self):
        temp_castle_rights = CastleRights(self.curr_castling_rights.wk, self.curr_castling_rights.bk,
                                          self.curr_castling_rights.wq, self.curr_castling_rights.bq)
        moves = []
        self.is_in_check, self.pins, self.checks = self.check_pins_and_checks()

        if self.white_move:
            king_row = self.white_king_loc[0]
            king_col = self.white_king_loc[1]
        else:
            king_row = self.black_king_loc[0]
            king_col = self.black_king_loc[1]
        if self.is_in_check:
            if len(self.checks) == 1:
                moves = self.get_possible_moves()
                check = self.checks[0]
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col]
                valid_squares = []
                if piece_checking[1] == "N":
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i,
                                        king_col + check[3] * i)
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[
                            1] == check_col:
                            break
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].piece_moved[1] != "K":
                        if not (moves[i].end_row,
                                moves[i].end_col) in valid_squares:
                            moves.remove(moves[i])
            else:
                self.get_king_moves(king_row, king_col, moves)
        else:
            moves = self.get_possible_moves()
            if self.white_move:
                self.get_castle_moves(self.white_king_loc[0], self.white_king_loc[1], moves)
            else:
                self.get_castle_moves(self.black_king_loc[0], self.black_king_loc[1], moves)

        if len(moves) == 0:
            if self.in_check():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False

        self.curr_castling_rights = temp_castle_rights
        return moves

    def in_check(self):
        if self.white_move:
            return self.square_under_attack(self.white_king_loc[0], self.white_king_loc[1])
        else:
            return self.square_under_attack(self.black_king_loc[0], self.black_king_loc[1])

    def update_castle_rights(self, move):
        if move.piece_captured == "wR":
            if move.end_col == 0:
                self.curr_castling_rights.wq = False
            elif move.end_col == 7:
                self.curr_castling_rights.wk = False
        elif move.piece_captured == "bR":
            if move.end_col == 0:
                self.curr_castling_rights.bq = False
            elif move.end_col == 7:
                self.curr_castling_rights.bk = False

        if move.piece_moved == 'wK':
            self.curr_castling_rights.wq = False
            self.curr_castling_rights.wk = False
        elif move.piece_moved == 'bK':
            self.curr_castling_rights.bq = False
            self.curr_castling_rights.bk = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:
                    self.curr_castling_rights.wq = False
                elif move.start_col == 7:
                    self.curr_castling_rights.wk = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:
                    self.curr_castling_rights.bq = False
                elif move.start_col == 7:
                    self.curr_castling_rights.bk = False

    def square_under_attack(self, row, col):
        self.white_move = not self.white_move
        opponents_moves = self.get_possible_moves()
        self.white_move = not self.white_move
        for move in opponents_moves:
            if move.end_row == row and move.end_col == col:
                return True
        return False


    def check_pins_and_checks(self):
        pins = []
        checks = []
        is_in_check = False
        if self.white_move:
            enemy_color = "b"
            friendly_color = "w"
            start_row = self.white_king_loc[0]
            start_col = self.white_king_loc[1]
        else:
            enemy_color = "w"
            friendly_color = "b"
            start_row = self.black_king_loc[0]
            start_col = self.black_king_loc[1]
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            direction = directions[j]
            possible_pin = ()
            for i in range(1, 8):
                end_row = start_row + direction[0] * i
                end_col = start_col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == friendly_color and end_piece[1] != "K":
                        if possible_pin == ():
                            possible_pin = (end_row, end_col, direction[0], direction[1])
                        else:
                            break
                    elif end_piece[0] == enemy_color:
                        enemy_type = end_piece[1]
                        if (0 <= j <= 3 and enemy_type == "R") or (4 <= j <= 7 and enemy_type == "B") or (
                                i == 1 and enemy_type == "p" and (
                                (enemy_color == "w" and 6 <= j <= 7) or (enemy_color == "b" and 4 <= j <= 5))) or (
                                enemy_type == "Q") or (i == 1 and enemy_type == "K"):
                            if possible_pin == ():
                                is_in_check = True
                                checks.append((end_row, end_col, direction[0], direction[1]))
                                break
                            else:
                                pins.append(possible_pin)
                                break
                        else:
                            break
                else:
                    break
        knight_moves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
        for move in knight_moves:
            end_row = start_row + move[0]
            end_col = start_col + move[1]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == "N":
                    is_in_check = True
                    checks.append((end_row, end_col, move[0], move[1]))
        return is_in_check, pins, checks

    def get_knight_moves(self, row, col, moves):
        piece_pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break
        #L shaped
        knight_moves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2),
                        (1, -2))
        friendly_color = "w" if self.white_move else "b"
        for move in knight_moves:
            end_row = row + move[0]
            end_col = col + move[1]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != friendly_color:
                        moves.append(Move((row, col), (end_row, end_col), self.board))

    def get_pawn_moves(self, row, col, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.white_move:
            move_amount = -1
            start_row = 6
            enemy_color = "b"
            king_row, king_col = self.white_king_loc
        else:
            move_amount = 1
            start_row = 1
            enemy_color = "w"
            king_row, king_col = self.black_king_loc

        if self.board[row + move_amount][col] == "**":
            if not piece_pinned or pin_direction == (move_amount, 0):
                moves.append(Move((row, col), (row + move_amount, col), self.board))
                if row == start_row and self.board[row + 2 * move_amount][col] == "**":
                    moves.append(Move((row, col), (row + 2 * move_amount, col), self.board))
        if col - 1 >= 0:
            if not piece_pinned or pin_direction == (move_amount, -1):
                if self.board[row + move_amount][col - 1][0] == enemy_color:
                    moves.append(Move((row, col), (row + move_amount, col - 1), self.board))
                if (row + move_amount, col - 1) == self.can_enpassant:
                    attacking_piece = blocking_piece = False
                    if king_row == row:
                        if king_col < col:
                            inside_range = range(king_col + 1, col - 1)
                            outside_range = range(col + 1, 8)
                        else:
                            inside_range = range(king_col - 1, col, -1)
                            outside_range = range(col - 2, -1, -1)
                        for i in inside_range:
                            if self.board[row][i] != "**":
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[row][i]
                            if square[0] == enemy_color and (square[1] == "R" or square[1] == "Q"):
                                attacking_piece = True
                            elif square != "**":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((row, col), (row + move_amount, col - 1), self.board, is_enpassant=True))
        if col + 1 <= 7:
            if not piece_pinned or pin_direction == (move_amount, +1):
                if self.board[row + move_amount][col + 1][0] == enemy_color:
                    moves.append(Move((row, col), (row + move_amount, col + 1), self.board))
                if (row + move_amount, col + 1) == self.can_enpassant:
                    attacking_piece = blocking_piece = False
                    if king_row == row:
                        if king_col < col:
                            inside_range = range(king_col + 1, col)
                            outside_range = range(col + 2, 8)
                        else:
                            inside_range = range(king_col - 1, col + 1, -1)
                            outside_range = range(col - 1, -1, -1)
                        for i in inside_range:
                            if self.board[row][i] != "**":
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[row][i]
                            if square[0] == enemy_color and (square[1] == "R" or square[1] == "Q"):
                                attacking_piece = True
                            elif square != "**":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((row, col), (row + move_amount, col + 1), self.board, is_enpassant=True))

    def get_rook_moves(self, row, col, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[row][col][
                    1] != "Q":
                    self.pins.remove(self.pins[i])
                break

        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemy_color = "b" if self.white_move else "w"
        for direction in directions:
            for i in range(1, 8):
                end_row = row + direction[0] * i
                end_col = col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                    if not piece_pinned or pin_direction == direction or pin_direction == (
                            -direction[0], -direction[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "**":
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break
                        else:
                            break
                else:
                    break


    def get_bishop_moves(self, row, col, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        directions = ((-1, -1), (-1, 1), (1, 1), (1, -1))
        enemy_color = "b" if self.white_move else "w"
        for direction in directions:
            for i in range(1, 8):
                end_row = row + direction[0] * i
                end_col = col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                    if not piece_pinned or pin_direction == direction or pin_direction == (
                            -direction[0], -direction[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == "**":
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_color:
                            moves.append(Move((row, col), (end_row, end_col), self.board))
                            break
                        else:
                            break
                else:
                    break


    def get_king_moves(self, row, col, moves):
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        friendly_color = "w" if self.white_move else "b"
        for i in range(8):
            end_row = row + row_moves[i]
            end_col = col + col_moves[i]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != friendly_color:
                    if friendly_color == "w":
                        self.white_king_loc = (end_row, end_col)
                    else:
                        self.black_king_loc = (end_row, end_col)
                    is_in_check, pins, checks = self.check_pins_and_checks()
                    if not is_in_check:
                        moves.append(Move((row, col), (end_row, end_col), self.board))
                    if friendly_color == "w":
                        self.white_king_loc = (row, col)
                    else:
                        self.black_king_loc = (row, col)

    def get_queen_moves(self, row, col, moves):
        # use previous methods
        self.get_bishop_moves(row, col, moves)
        self.get_rook_moves(row, col, moves)

    def get_castle_moves(self, row, col, moves):
        if self.square_under_attack(row, col):
            return
        if (self.white_move and self.curr_castling_rights.wk) or (
                not self.white_move and self.curr_castling_rights.bk):
            self.get_king_castle_moves(row, col, moves)
        if (self.white_move and self.curr_castling_rights.wq) or (
                not self.white_move and self.curr_castling_rights.bq):
            self.get_queen_castle_moves(row, col, moves)



    def get_king_castle_moves(self, row, col, moves):
        if self.board[row][col + 1] == '**' and self.board[row][col + 2] == '**':
            if not self.square_under_attack(row, col + 1) and not self.square_under_attack(row, col + 2):
                moves.append(Move((row, col), (row, col + 2), self.board, is_castle_move=True))

    def get_queen_castle_moves(self, row, col, moves):
        if self.board[row][col - 1] == '**' and self.board[row][col - 2] == '**' and self.board[row][col - 3] == '**':
            if not self.square_under_attack(row, col - 1) and not self.square_under_attack(row, col - 2):
                moves.append(Move((row, col), (row, col - 2), self.board, is_castle_move=True))



