import pygame as pg
import engine 

OFFSET = 100
WIDTH = HEIGHT = 520 + 2 * OFFSET 
DIMENSION = 8
SQUARE_SIZE = (WIDTH - 2 * OFFSET)//DIMENSION
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
            pg.draw.rect(screen, color, pg.Rect(OFFSET + c*SQUARE_SIZE, (3 * OFFSET)//2 + r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != '--':
                screen.blit(IMAGES[piece], pg.Rect(OFFSET + c*SQUARE_SIZE-2, (3*OFFSET)//2 +r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_transparent_rect(screen, color, rect, alpha):
    # Create a temporary surface with per-pixel alpha
    temp_surface = pg.Surface((rect[2], rect[3]), pg.SRCALPHA)
    # Fill the surface with the desired color and alpha
    temp_surface.fill((*color, alpha))
    # Blit the temporary surface onto the main screen
    screen.blit(temp_surface, rect.topleft)

def highlight_pieces(r, c, legal_moves, screen, gs):
    piece = gs.board[r][c]
    enemy_color = "b" if gs.white_to_move else "w"

    if piece != '--':
        if piece[0] != enemy_color:
            draw_transparent_rect(screen, (0, 255, 0), pg.Rect(OFFSET + c*SQUARE_SIZE, (3 * OFFSET)//2 + r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 200)
            screen.blit(IMAGES[piece], pg.Rect(OFFSET + c*SQUARE_SIZE-2, (3 * OFFSET)//2 + r*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    for move in legal_moves:
        if move.start_row == r and move.start_col == c:
            piece = gs.board[move.end_row][move.end_col]
            draw_transparent_rect(screen, (0, 255, 0), pg.Rect(OFFSET + move.end_col*SQUARE_SIZE, (3 * OFFSET)//2 + move.end_row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 100)
            #pg.draw.rect(screen, 'green', pg.Rect(OFFSET + move.end_col*SQUARE_SIZE, (3 * OFFSET)//2 + move.end_row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            if piece != '--':
                screen.blit(IMAGES[piece], pg.Rect(OFFSET + move.end_col*SQUARE_SIZE-2, (3 * OFFSET)//2 + move.end_row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    pg.display.flip()

def draw_gs(screen, gs):
    draw_chess_board_pattern(screen)
    draw_pieces(screen, gs.board)

def draw_pawn_promotion_window(screen, gs):
    pg.draw.rect(screen, 'white', pg.Rect(WIDTH//2 - 150, 30, 300, 70))

    if gs.white_to_move:
        pieces = ['wQ', 'wR', 'wB', 'wN']
    else:
        pieces = ['bQ', 'bR', 'bB', 'bN']

    # Display the promotion pieces
    x_offset = WIDTH//2 - 140
    for piece in pieces:
        screen.blit(IMAGES[piece], (x_offset, 35))
        x_offset += 70

    pg.display.flip()

    # Wait for the player to select a piece
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                return None

            if event.type == pg.MOUSEBUTTONDOWN:
                x, y = event.pos
                if 30 <= y <= 110:
                    screen.fill(pg.Color('black'))
                    draw_gs(screen, gs)
                    if WIDTH//2 - 140 <= x <= WIDTH//2 - 70:
                        return pieces[0][1]  # Queen
                    elif WIDTH//2 - 70 <= x <= WIDTH//2:
                        return pieces[1][1]  # Rook
                    elif WIDTH//2 <= x <= WIDTH//2 + 70:
                        return pieces[2][1]  # Bishop
                    elif WIDTH//2 + 70 <= x <= WIDTH//2 + 140:
                        return pieces[3][1]  # Knight

def draw_result(screen, result):
    font = pg.font.SysFont('Arial', 30)  
    text_surface = font.render(result, True, (255, 255, 255))
    text_rect = text_surface.get_rect()
    text_rect.center = (WIDTH // 2, HEIGHT - 650)
    screen.blit(text_surface, text_rect)

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
                c = (location[0] - (OFFSET))// SQUARE_SIZE
                r = (location[1] - (3 * OFFSET)//2)//SQUARE_SIZE
                if c not in range(0, 8) or r not in range(0, 8):
                    continue
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
                            if legal_move.pawn_promotion:
                                promotion_piece = draw_pawn_promotion_window(screen, gs)
                                legal_move = engine.Move(player_clicks[0], player_clicks[1], gs.board, pawn_promotion=promotion_piece)
                            gs.make_move(legal_move)
                            print(move.get_chess_notation())
                            move_made = True
                            break
                    else:
                        draw_gs(screen, gs)
                    sq_selected = ()
                    player_clicks = []
        
        if move_made:
            if gs.plys_without_captures_or_pawn_moves() >= 100:
                draw_result(screen, "Draw by 50-move rule!")

            if gs.three_fold_repetition():
                draw_result(screen, "Draw by three fold repetition!")
                
            legal_moves = gs.get_legal_moves()
            if len(legal_moves) == 0:
                draw_result(screen, gs.determine_mate_or_stalemate())
            move_made = False
            draw_gs(screen, gs)
            print(gs.fen()[:-4])
        clock.tick(MAX_FPS)
        pg.display.flip()


if __name__ == '__main__':
    main()