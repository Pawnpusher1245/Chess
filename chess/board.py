from pieces import Piece

wp = Piece('w', 'p')
wn = Piece('w', 'n')
wb = Piece('w', 'b')
wr = Piece('w', 'r')
wq = Piece('w', 'q')
wk = Piece('w', 'k')

bp = Piece('b', 'p')
bn = Piece('b', 'n')
bb = Piece('b', 'b')
br = Piece('b', 'r')
bq = Piece('b', 'q')
bk = Piece('b', 'k')

class Board:
    def __init__(self) -> None:    
        self.board = [['x ' for _ in range(8)] for _ in range(8)]
        self.board[0] = [br, bn, bb, bq, bk, bb, bn, br]
        self.board[1] = [bp for i in range(8)]
        self.board[6] = [wp for i in range(8)]
        self.board[7] = [wr, wn, wb, wq, wk, wb, wn, wr]
        self.turn = 0

    def __str__(self):
        board_str = ''
        for row in self.board:
            # Convert each Piece object to its string representation
            row_str = [str(piece) for piece in row]
            board_str += ' '.join(row_str) + '\n'
        return board_str

    def make_move(self, from_index, to_index):
        letter_map = {'a' : 0, 'b':1, 'c':2, 'd':3, 'e':4, 'f':5, 'g':6, 'h':7}
        from_index = list(from_index)
        to_index = list(to_index)

        piece = self.board[8-int(from_index[1])][letter_map[from_index[0]]]
        self.board[8-int(from_index[1])][letter_map[from_index[0]]] = 'x '
        self.board[8-int(to_index[1])][letter_map[to_index[0]]] = piece
        self.turn = not self.turn

    def find_squares_with_piece(self, squares, piece):
        squares_with_piece = []
        for square in squares:
            row, col = square
            if self.board[row][col] == piece:
                squares_with_piece.append(square)
        return squares_with_piece

    def is_empty(self, row, col):
        if self.board[row][col] == 'x ':
            return True
        return False

    def squares_color_pieces(self):
        squares = []
        for i in range(8):
            for j in range(8):
                # Check if the square is not empty and matches the color
                if self.board[i][j] != 'x ' and self.board[i][j].color == ('w' if self.turn == 0 else 'b'):
                    squares.append((i, j))
        return squares
    
    def turn_to_move(self):
        if self.turn:
            return 'w'
        return 'b'

    def legal_pawn_move(self, squares):
        pass

    def legal_knight_moves(self, squares):
        legal_n_moves = []
        for square in squares:
            row, col = square  # Unpack the square into row and column
            if self.board[row][col].type == 'n':
                 # Generate all possible knight moves
                possible_moves = [(row - 2, col - 1), (row - 2, col + 1), 
                                (row - 1, col - 2), (row - 1, col + 2), 
                                (row + 2, col - 1), (row + 2, col + 1), 
                                (row + 1, col - 2), (row + 1, col + 2)]
                # Filter out moves outside the board boundaries
                legal_n_moves.extend(((row, col), (r, c)) for r, c in possible_moves if 0 <= r < 8 and 0 <= c < 8 and (self.board[r][c] == 'x ' or self.board[r][c].color != self.board[row][col].color))
        return legal_n_moves
    
    def legal_bishop_moves(self, squares):
        pass
    
    def legal_rook_moves(self, squares):
        possible_moves = []
        squares_with_rook = self.find_squares_with_piece(squares)
        for square in squares_with_rook:
            row, col = square
            # Horizontal moves
            row_to = row + 1
            while row_to <= 7:
                if self.board[row_to][col] != 'x ':
                    if self.board[row_to][col].color



    def legal_queen_moves(self, squares):
        pass

    def legal_king_moves(self, squares):
        legal_k_moves = []
        for square in squares:
            row, col = square  # Unpack the square into row and column
            if self.board[row][col].type == 'k':
                    # Generate all possible knight moves
                possible_moves = [(row, col - 1), (row, col + 1), 
                                (row + 1, col - 1), (row + 1, col), (row + 1, col - 1), 
                                (row - 1, col - 1), (row - 1, col), (row - 1, col + 1)]
                # Filter out moves outside the board boundaries
                legal_k_moves.extend(((row, col), (r, c)) for r, c in possible_moves if 0 <= r < 8 and 0 <= c < 8 and (self.board[r][c] == 'x ' or self.board[r][c].color != self.board[row][col].color))
        return legal_k_moves

    def fen(self):
        pass

if __name__ == '__main__':
    a = Board()
    a.make_move('e2', 'e4')
    a.make_move('c2', 'c3')
    print(a)

    print(a.legal_knight_moves(a.squares_color_pieces()))
