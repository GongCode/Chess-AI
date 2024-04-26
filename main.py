"""
Main driver
user input.
"""
import sys
from multiprocessing import Process, Queue
import pygame as p
import engine, ChessBot

IMAGES = {}
FPS = 30
PY_BOARD_WIDTH = 512
PY_BOARD_HEIGHT = 512
MOVE_PANEL_WIDTH = 264
MOVE_PANEL_HEIGHT = PY_BOARD_HEIGHT
DIMENSIONS = 8
SQ_SIZE = PY_BOARD_HEIGHT // DIMENSIONS


def main():
    # user input and graphics
    p.init()
    player1 = True
    player2 = False
    game_running = True
    game_ended = False
    bot_thinking = False
    screen = p.display.set_mode((PY_BOARD_WIDTH + MOVE_PANEL_WIDTH, PY_BOARD_HEIGHT))
    screen.fill(p.Color("white"))
    clock = p.time.Clock()
    game_state = engine.GameState()
    valid_moves = game_state.get_valid_moves()
    sq_selected = ()  
    sq_clicks = [] 
    load_img()  
    log_font = p.font.SysFont("Arial", 14, False, False)
    ai_process = None
    move_made = False  
    move_undo = False
    animate = False  

    while game_running:
        human_move = (game_state.white_move and player1) or (not game_state.white_move and player2)
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                sys.exit()
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_ended:
                    location = p.mouse.get_pos()  
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sq_selected == (row, col) or col >= 8:
                        # deselecting
                        sq_selected = ()  
                        sq_clicks = [] 
                    else:
                        sq_selected = (row, col)
                        sq_clicks.append(sq_selected)  
                    if len(sq_clicks) == 2 and human_move:  
                        move = engine.Move(sq_clicks[0], sq_clicks[1], game_state.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                game_state.make_move(valid_moves[i])
                                move_made = True
                                animate = True
                                sq_selected = () 
                                sq_clicks = []
                        if not move_made:
                            sq_clicks = [sq_selected]

            elif e.type == p.KEYDOWN:
                # undo move on Z
                if e.key == p.K_z:  
                    game_state.undo_move()
                    move_made = True
                    animate = False
                    game_ended = False
                    if bot_thinking:
                        ai_process.terminate()
                        bot_thinking = False
                    move_undo = True
                    # resets game on R
                if e.key == p.K_r:  
                    game_state = engine.GameState()
                    valid_moves = game_state.get_valid_moves()
                    sq_selected = ()
                    sq_clicks = []
                    move_made = False
                    animate = False
                    game_ended = False
                    if bot_thinking:
                        ai_process.terminate()
                        bot_thinking = False
                    move_undo = True

        if not game_ended and not human_move and not move_undo:
            if not bot_thinking:
                bot_thinking = True
                return_queue = Queue()  
                ai_process = Process(target=ChessBot.find_best_move, args=(game_state, valid_moves, return_queue))
                ai_process.start()

            if not ai_process.is_alive():
                ai_move = return_queue.get()
                if ai_move is None:
                    ai_move = ChessBot.find_random_move(valid_moves)
                game_state.make_move(ai_move)
                move_made = True
                animate = True
                bot_thinking = False

        if move_made:
            if animate:
                animate_move(game_state.move_log[-1], screen, game_state.board, clock)
            valid_moves = game_state.get_valid_moves()
            move_made = False
            animate = False
            move_undo = False

        draw_game_state(screen, game_state, valid_moves, sq_selected)

        if not game_ended:
            draw_move_log(screen, game_state, log_font)

        if game_state.checkmate:
            game_ended = True
            if game_state.white_move:
                draw_end_text(screen, "Black wins by checkmate")
            else:
                draw_end_text(screen, "White wins by checkmate")

        elif game_state.stalemate:
            game_ended = True
            draw_end_text(screen, "Stalemate")

        clock.tick(FPS)
        p.display.flip()


def draw_board(screen):
    global colors    # colors = [p.Color("lightyellow2"), p.Color("darkolivegreen4")]

    colors = [p.Color("wheat"), p.Color("tan3")]
    # colors = [p.Color("white"), p.Color("gray")]



    for row in range(DIMENSIONS):
        for column in range(DIMENSIONS):
            color = colors[((row + column) % 2)]
            p.draw.rect(screen, color, p.Rect(column * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_pieces(screen, board):
    # use curr game state to draw the board
    for row in range(DIMENSIONS):
        for column in range(DIMENSIONS):
            piece = board[row][column]
            if piece != "**":
                screen.blit(IMAGES[piece], p.Rect(column * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def draw_game_state(screen, game_state, valid_moves, sq_selected):
    draw_board(screen)  
    highlight_squares(screen, game_state, valid_moves, sq_selected)
    draw_pieces(screen, game_state.board)  


def highlight_squares(screen, game_state, valid_moves, sq_selected):
    if (len(game_state.move_log)) > 0:
        last_move = game_state.move_log[-1]
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.set_alpha(100)
        s.fill(p.Color('green'))
        screen.blit(s, (last_move.end_col * SQ_SIZE, last_move.end_row * SQ_SIZE))
    if sq_selected != ():
        row, col = sq_selected
        if game_state.board[row][col][0] == (
                'w' if game_state.white_move else 'b'):  
            # highlighting
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)  
            s.fill(p.Color('blue'))
            screen.blit(s, (col * SQ_SIZE, row * SQ_SIZE))
            s.fill(p.Color('yellow'))
            for move in valid_moves:
                if move.start_row == row and move.start_col == col:
                    screen.blit(s, (move.end_col * SQ_SIZE, move.end_row * SQ_SIZE))


def animate_move(move, screen, board, clock):
    global colors
    d_row = move.end_row - move.start_row
    d_col = move.end_col - move.start_col
    frames_per_square = 10
    frame_count = (abs(d_row) + abs(d_col)) * frames_per_square
    for frame in range(frame_count + 1):
        row, col = (move.start_row + d_row * frame / frame_count, move.start_col + d_col * frame / frame_count)
        draw_board(screen)
        draw_pieces(screen, board)
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col * SQ_SIZE, move.end_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)
        if move.piece_captured != '**':
            if move.is_enpassant:
                enpassant_row = move.end_row + 1 if move.piece_captured[0] == 'b' else move.end_row - 1
                end_square = p.Rect(move.end_col * SQ_SIZE, enpassant_row * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.piece_captured], end_square)
        # animating moves
        screen.blit(IMAGES[move.piece_moved], p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)


def draw_end_text(screen, text):
    font = p.font.SysFont("Helvetica", 32, True, False)
    text_object = font.render(text, False, p.Color("gray"))
    text_location = p.Rect(0, 0, PY_BOARD_WIDTH, PY_BOARD_HEIGHT).move(PY_BOARD_WIDTH / 2 - text_object.get_width() / 2,
                                                                 PY_BOARD_HEIGHT / 2 - text_object.get_height() / 2)
    screen.blit(text_object, text_location)
    text_object = font.render(text, False, p.Color('black'))
    screen.blit(text_object, text_location.move(2, 2))
def draw_move_log(screen, game_state, font):
    move_log_rect = p.Rect(PY_BOARD_WIDTH, 0, MOVE_PANEL_WIDTH, MOVE_PANEL_HEIGHT)
    p.draw.rect(screen, p.Color('black'), move_log_rect)
    move_log = game_state.move_log
    move_texts = []
    for i in range(0, len(move_log), 2):
        move_string = str(i // 2 + 1) + '. ' + str(move_log[i]) + " "
        if i + 1 < len(move_log):
            move_string += str(move_log[i + 1]) + "  "
        move_texts.append(move_string)

    moves_per_row = 3
    padding = 5
    line_spacing = 2
    text_y = padding
    for i in range(0, len(move_texts), moves_per_row):
        text = ""
        for j in range(moves_per_row):
            if i + j < len(move_texts):
                text += move_texts[i + j]

        text_object = font.render(text, True, p.Color('white'))
        text_location = move_log_rect.move(padding, text_y)
        screen.blit(text_object, text_location)
        text_y += text_object.get_height() + line_spacing

"""
    Will be called once to load image
"""
def load_img():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("img/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))



if __name__ == "__main__":
    main()