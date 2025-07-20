import pygame as pg
import engine 

WIDTH = HEIGHT = 520 + 200 
DIMENSION = 8
SQUARE_SIZE = (WIDTH - 200)//DIMENSION
MAX_FPS = 15
IMAGES = {}

def load_images():
    pieces = ['wp', 'wN', 'wB', 'wR', 'wQ', 'wK', 'bp', 'bN', 'bB', 'bR', 'bQ', 'bK']
    for piece in pieces:
        IMAGES[piece] = pg.transform.scale(pg.image.load(f'images/{piece}.png'), (SQUARE_SIZE, SQUARE_SIZE))

def draw_chess_board_pattern(screen):
    colors = [pg.Color('white'), pg.Color('grey')]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r+c)%2]
            pg.draw.rect(screen, color, pg.Rect(100 + c*SQUARE_SIZE, 150 + r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':
                screen.blit(IMAGES[piece], pg.Rect(100 + c*SQUARE_SIZE-2, 150 +r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def highlight_pieces(r, c, legal_moves, screen, gs):
    piece = gs.board[r][c]
    enemy_color = "b" if gs.white_to_move else "w"

    if piece != '--':
        if piece[0] != enemy_color:
            pg.draw.rect(screen, 'green', pg.Rect(c*SQUARE_SIZE, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            screen.blit(IMAGES[piece], pg.Rect(c*SQUARE_SIZE-2, r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    for move in legal_moves:
        if move.start_row == r and move.start_col == c:
            piece = gs.board[move.end_row][move.end_col]
            pg.draw.rect(screen, 'green', pg.Rect(move.end_col*SQUARE_SIZE, move.end_row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            if piece != '--':
                screen.blit(IMAGES[piece], pg.Rect(move.end_col*SQUARE_SIZE-2, move.end_row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    pg.display.flip()

def draw_gs(screen, gs):
    draw_chess_board_pattern(screen)
    draw_pieces(screen, gs.board)

def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    screen.fill(pg.Color('black'))
    clock = pg.time.Clock()
    gs = engine.GameState()
    load_images()
    sq_selected = () # Keeps track of latest clicked square
    player_clicks =[] # Stores two tuples representing two latest clicks
    legal_moves = gs.get_legal_moves()
    move_made = False # flag variable to flag for a move being made

    running = True
    draw_gs(screen, gs)

    while running:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_z:
                    gs.undo_move()
                    move_made = True
            elif e.type == pg.MOUSEBUTTONDOWN:
                location = pg.mouse.get_pos()
                c = location[0] // SQUARE_SIZE
                r = location[1] //SQUARE_SIZE
                if sq_selected == (r, c): # The user clicked same square twice, undoing the click
                    sq_selected = ()
                    player_clicks = []
                    draw_gs(screen, gs)
                else:
                    sq_selected = (r, c)
                    player_clicks.append(sq_selected)
                    if len(player_clicks) == 1:
                        highlight_pieces(r, c, legal_moves, screen, gs)                   
                
                if len(player_clicks) == 2:
                    move = engine.Move(player_clicks[0], player_clicks[1], gs.board)
                    for legal_move in legal_moves:
                        if move == legal_move:
                            gs.make_move(legal_move)
                            print(move.get_chess_notation())
                            move_made = True
                    else:
                        draw_gs(screen, gs)
                    sq_selected = ()
                    player_clicks = []
        
        if move_made:
            legal_moves = gs.get_legal_moves()
            move_made = False
            draw_gs(screen, gs)
        clock.tick(MAX_FPS)
        pg.display.flip()


if __name__ == '__main__':
    main()