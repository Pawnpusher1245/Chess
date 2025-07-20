class GameState():
    def __init__(self) -> None:
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]

        self.white_to_move = True
        self.log = []
        
    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.log.append(move)
        self.white_to_move = not self.white_to_move

    def undo_move(self):
        """Undo the last move made"""
        if len(self.log) != 0:
            move = self.log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move

    def check_directions_until_stop(self, r, c, directions, moves):
        """Checks and appends all moves in a direction until it reaches enemy or ally piece"""
        enemy_color = "b" if self.white_to_move else "w"

        for direction in directions:
            for i in range(1, 8):
                end_row = r + i * direction[0]
                end_col = c + i * direction[1]
                # Check if move is within the bounds of the board
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    # Check if the end square is empty or occupied by an opponent/allied piece
                    if end_piece == '--':
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif  end_piece[0] == enemy_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break

    def make_en_passant(self, r, c, pawn_to_be_taken_r, pawn_to_be_taken_c):
        """Function that makes the en passant move"""
        self.board[pawn_to_be_taken_r][pawn_to_be_taken_c] == '--'

        if self.white_to_move:
            move = Move((r,c), (pawn_to_be_taken_r - 1, pawn_to_be_taken_c), self.board)
            self.make_move(move)
        
        if not self.white_to_move:
            move = Move((r,c), (pawn_to_be_taken_r+1, pawn_to_be_taken_c), self.board)


    def get_pawn_moves(self, r, c, moves):
        if self.white_to_move:
            if self.board[r-1][c] == '--':
                moves.append(Move((r,c),(r-1, c), self.board))
                if r == 6:
                    if self.board[r-2][c] == '--':
                        moves.append(Move((r,c), (r-2,c), self.board))
            if c-1 >= 0:
                if self.board[r-1][c-1][0] == 'b':
                    moves.append(Move((r,c),(r-1,c-1),self.board))
            if c+1 <= 7:
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r,c),(r-1,c+1),self.board))
            # Check for en passant
            if r == 3:
                previous_move = self.log[-1]
                if previous_move.piece_moved == 'p' and previous_move.start_row == 1 and (previous_move.start_col == c+1 or previous_move.start_col == c-1) and previous_move.end_row == 3:
                    print("hi")
                    
        if not self.white_to_move:
            if self.board[r+1][c] == '--':
                moves.append(Move((r,c),(r+1, c), self.board))
                if r == 1:
                    moves.append(Move((r,c), (r+2,c), self.board))
            if c-1 >= 0:
                if self.board[r+1][c-1][0] == 'w':
                    moves.append(Move((r,c),(r+1,c-1),self.board))
            if c+1 <= 7:
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r,c),(r+1,c+1),self.board))
        # Check for en passant


    def get_knight_moves(self, r, c, moves):
        enemy_color = "b" if self.white_to_move else "w"
        knight_moves = [(2, 1), (2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2), (-2, 1), (-2, -1)]

        for move in knight_moves:
            end_row = r + move[0]
            end_col = c + move[1]
            
            # Check if move is within the bounds of the board
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                # Check if the end square is empty or occupied by an opponent's piece
                if end_piece == '--' or end_piece[0] == enemy_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_bishop_moves(self, r, c, moves):
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        self.check_directions_until_stop(r, c, directions, moves)

    def get_rook_moves(self, r, c, moves):
        directions = [(1,0), (0,1), (-1, 0), (0, -1)]
        self.check_directions_until_stop(r, c, directions, moves)    
    
    def get_queen_moves(self, r, c, moves):
        # Queen moves is just union of rook and bishop moves
        self.get_bishop_moves(r, c, moves)
        self.get_rook_moves(r, c, moves)

    def get_king_moves(self, r, c, moves):
        # List of all possible moves for a king
        king_moves = [
            (-1, -1), (-1, 0), (-1, 1),
            ( 0, -1),         ( 0, 1),
            ( 1, -1), ( 1, 0), ( 1, 1)
        ]
        
        enemy_color = 'b' if self.white_to_move else 'w'
        
        for move in king_moves:
            end_row = r + move[0]
            end_col = c + move[1]
            
            # Check if move is within the bounds of the board
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                # Check if the end square is empty or occupied by an opponent's piece
                if end_piece == '--' or end_piece[0] == enemy_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))



    def get_legal_moves(self):
        """All moves with considering checks (legal moves)
            - get all moves
            - play move
            - generate all possible moves for opposing player
            - if your king is not in check it is added to legal moves
        - return list of all legal moves
        """
        legal_moves = []
        turn = 'w' if self.white_to_move else 'b'
        moves = self.get_all_moves()

        
        for move in moves:
            appending = True # Variable that control whether to append or not
            self.make_move(move)
            for r in range(len(self.board)):
                for c in range(len(self.board[0])):
                    if self.board[r][c][0] == turn and self.board[r][c][1] == 'K':
                        king_row = r
                        king_col = c

            opponent_moves = self.get_all_moves()
            for opponent_move in opponent_moves:
                if opponent_move.end_row == king_row and opponent_move.end_col == king_col:
                    appending = False
            if appending:
                legal_moves.append(move)
            self.undo_move()
        return legal_moves
    
    def get_all_moves(self):
        """Generates all possibele moves without considering checks"""
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[r][c][1]
                    if piece == 'p':
                        self.get_pawn_moves(r, c, moves)
                    elif piece == 'N':
                        self.get_knight_moves(r, c, moves)
                    elif piece == 'B':
                        self.get_bishop_moves(r, c, moves)
                    elif piece == 'R':
                        self.get_rook_moves(r, c, moves)
                    elif piece == 'Q':
                        self.get_queen_moves(r, c, moves)
                    elif piece =='K':
                        self.get_king_moves(r, c, moves)
        return moves

class Move():
    # Conversion from chess notation to indices and reversed
    ranks_to_rows = {"1":7, "2": 6, "3": 5, "4": 4, 
                    "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e":4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, en_passant=False) -> None:
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.en_passant = en_passant
        self.move_ID = self.start_row*1000 + self.start_col*100 + self.end_row*10 + self.end_col

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_ID == other.move_ID
        return False

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + "-" + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]