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
        self.castle_rights_log = {}
        self.position_log = {"rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -" : 1}

        # Variables to check if castling is legal
        self.wkc = True
        self.wqc = True
        self.bkc = True
        self.bqc = True
        
    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.log.append(move)
        if move.en_passant:
            if self.white_to_move:
                self.board[move.end_row + 1][move.end_col] = "--"
            if not self.white_to_move:
                self.board[move.end_row - 1][move.end_col] = "--"

        if move.kc:
            self.board[move.end_row][move.end_col + 1] = "--"
            if self.white_to_move:
                self.board[move.end_row][move.end_col - 1] = "wR"
            if not self.white_to_move:
                self.board[move.end_row][move.end_col - 1] = "bR"
       
        if move.qc:
            self.board[move.end_row][move.end_col - 2] = "--"
            if self.white_to_move:
                self.board[move.end_row][move.end_col + 1] = "wR"
            else:
                self.board[move.end_row][move.end_col + 1] = "bR"

        if move.pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + move.pawn_promotion
        self.white_to_move = not self.white_to_move
        self.position_log[self.fen()[:-4]] = self.position_log.get(self.fen()[:-4], 0) + 1


    def undo_move(self):
        """Undo the last move made"""
        # Check castle rights
        castle = self.castle_rights_log.get(len(self.log), False)
        if castle:
            castle_mapping = {
                "wkc": ["wkc"],
                "wqc": ["wqc"],
                "wkcwqc": ["wkc", "wqc"],
                "bkc" : ["bkc"],
                "bqc" : ["bqc"],
                "bkcbqc" : ["bkc, bqc"]
            }
            
            for attr in castle_mapping.get(castle, []):
                setattr(self, attr, True)

        if len(self.log) != 0:
            move = self.log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            if move.en_passant:
                if self.white_to_move:
                    self.board[move.end_row - 1][move.end_col] = "wp"
                else:
                    self.board[move.end_row + 1][move.end_col] = "bp"

            if move.kc:
                self.board[move.end_row][move.end_col - 1] = "--"
                if self.white_to_move:
                    self.board[move.end_row][move.end_col + 1] = "bR"
                else:
                    self.board[move.end_row][move.end_col + 1] = "wR"

            if move.qc:
                self.board[move.end_row][move.end_col + 1] = "--"
                if self.white_to_move:
                    self.board[move.end_row][move.end_col - 2] = "bR"
                else:
                    self.board[move.end_row][move.end_col - 2] = "wR" 
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
    def check_for_kc(self, r, c, opponent_moves):
        """Checks that no kingside castling square is attacked and that they are all empty"""
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            appending = True
            for move in opponent_moves:
                if move.end_row == r:
                    if move.end_col in [c, c+1, c+2]:
                        appending = False
                        break
            return appending
        
    def check_for_qc(self, r, c, opponent_moves):
        """Checks that no queenside castling square is attacked and that they are all empty"""
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--":
            appending = True
            for move in opponent_moves:
                if move.end_row == r:
                    if move.end_col in [c, c-1, c-2]:
                        appending = False
            return appending 


    def get_pawn_moves(self, r, c, moves):
        if self.white_to_move:
            if self.board[r-1][c] == '--':
                # Single step move
                if r == 1:
                    # Pawn promotion on reaching the last rank
                    for promotion_piece in ['N', 'B', 'R', 'Q']:
                        moves.append(Move((r, c), (r-1, c), self.board, pawn_promotion=promotion_piece))
                else:
                    moves.append(Move((r, c), (r-1, c), self.board))
                    # Double step move from starting position
                    if r == 6 and self.board[r-2][c] == '--':
                        moves.append(Move((r, c), (r-2, c), self.board))
            
            # Captures
            if c-1 >= 0:  # Capture to the left
                if self.board[r-1][c-1][0] == 'b':
                    if r == 1:
                        for promotion_piece in ['N', 'B', 'R', 'Q']:
                            moves.append(Move((r, c), (r-1, c-1), self.board, pawn_promotion=promotion_piece))
                    else:
                        moves.append(Move((r, c), (r-1, c-1), self.board))
            if c+1 <= 7:  # Capture to the right
                if self.board[r-1][c+1][0] == 'b':
                    if r == 1:
                        for promotion_piece in ['N', 'B', 'R', 'Q']:
                            moves.append(Move((r, c), (r-1, c+1), self.board, pawn_promotion=promotion_piece))
                    else:
                        moves.append(Move((r, c), (r-1, c+1), self.board))
            
            # En passant
            if r == 3:
                previous_move = self.log[-1]
                if previous_move.piece_moved == 'bp' and previous_move.start_row == 1 and previous_move.end_row == 3:
                    if previous_move.start_col == c+1 and self.board[r][c+1] == 'bp':
                        moves.append(Move((r, c), (r-1, c+1), self.board, en_passant=True))
                    elif previous_move.start_col == c-1 and self.board[r][c-1] == 'bp':
                        moves.append(Move((r, c), (r-1, c-1), self.board, en_passant=True))

        else:  # Black to move
            if self.board[r+1][c] == '--':
                # Single step move
                if r == 6:
                    # Pawn promotion on reaching the last rank
                    for promotion_piece in ['N', 'B', 'R', 'Q']:
                        moves.append(Move((r, c), (r+1, c), self.board, pawn_promotion=promotion_piece))
                else:
                    moves.append(Move((r, c), (r+1, c), self.board))
                    # Double step move from starting position
                    if r == 1 and self.board[r+2][c] == '--':
                        moves.append(Move((r, c), (r+2, c), self.board))
            
            # Captures
            if c-1 >= 0:  # Capture to the left
                if self.board[r+1][c-1][0] == 'w':
                    if r == 6:
                        for promotion_piece in ['N', 'B', 'R', 'Q']:
                            moves.append(Move((r, c), (r+1, c-1), self.board, pawn_promotion=promotion_piece))
                    else:
                        moves.append(Move((r, c), (r+1, c-1), self.board))
            if c+1 <= 7:  # Capture to the right
                if self.board[r+1][c+1][0] == 'w':
                    if r == 6:
                        for promotion_piece in ['N', 'B', 'R', 'Q']:
                            moves.append(Move((r, c), (r+1, c+1), self.board, pawn_promotion=promotion_piece))
                    else:
                        moves.append(Move((r, c), (r+1, c+1), self.board))
            
            # En passant
            if r == 4:
                previous_move = self.log[-1]
                if previous_move.piece_moved == 'wp' and previous_move.start_row == 6 and previous_move.end_row == 4:
                    if previous_move.start_col == c+1 and self.board[r][c+1] == 'wp':
                        moves.append(Move((r, c), (r+1, c+1), self.board, en_passant=True))
                    elif previous_move.start_col == c-1 and self.board[r][c-1] == 'wp':
                        moves.append(Move((r, c), (r+1, c-1), self.board, en_passant=True))


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

    def get_king_moves(self, r, c, moves, castling):
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
        
        if castling:
            # Check for castling possibility
            # First check that castling squares are not attacked to do this we must generate all opponent moves
            self.white_to_move = not self.white_to_move
            opponent_moves = self.get_all_moves(castling=False)
            self.white_to_move = not self.white_to_move

            if self.white_to_move:
                if self.wkc:
                    appending = self.check_for_kc(r, c, opponent_moves)
                    if appending:
                        moves.append(Move((r, c), (r, c+2), self.board, kc=True))
                    
                if self.wqc:
                    appending = self.check_for_qc(r, c, opponent_moves)
                    if appending:
                        moves.append(Move((r,c), (r, c-2), self.board, qc=True))
            
            if not self.white_to_move:
                if self.bkc:
                    appending = self.check_for_kc(r, c, opponent_moves)
                    if appending:
                        moves.append(Move((r, c), (r, c+2), self.board, kc=True))

                if self.bqc:
                    appending = self.check_for_qc(r, c, opponent_moves)
                    if appending:
                        moves.append(Move((r,c), (r, c-2), self.board, qc=True))


    def get_legal_moves(self):
        """All moves with considering checks (legal moves)
            - get all moves
            - play move
            - generate all possible moves for opposing player
            - if your king is not in check it is added to legal moves
        - return list of all legal moves
        """
        # Handle if castling has become illegal
        if self.board[7][7] != "wR":
            if self.wkc:
                self.castle_rights_log[len(self.log)] = "wkc"
                self.wkc = False
        if self.board[7][0] != "wR":
            if self.wqc:
                self.castle_rights_log[len(self.log)] = "wqc"
                self.wqc = False
        if self.board[7][4] != "wK":
            if self.wkc and self.wqc:
                self.castle_rights_log[len(self.log)] = "wkcwqc"
            elif self.wkc:
                self.castle_rights_log[len(self.log)] = "wkc"
            elif self.wqc:
                self.castle_rights_log[len(self.log)] = "wqc"
            self.wkc = False
            self.wqc = False

        if self.board[0][7] != "bR":
            if self.bkc:
                self.castle_rights_log[len(self.log)] = "bkc"
                self.bkc = False  
        if self.board[0][0] != "bR":
            if self.bqc:
                self.castle_rights_log[len(self.log)] = "bqc"
                self.wqc = False
        if self.board[0][4] != "bK":
            if self.bkc and self.bqc:
                self.castle_rights_log[len(self.log)] = "bkcbqc"
            elif self.bkc:
                self.castle_rights_log[len(self.log)] = "bkc"
            elif self.bqc:
                self.castle_rights_log[len(self.log)] = "bqc"
            self.bkc = False
            self.bqc = False
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

            opponent_moves = self.get_all_moves(castling=False)
            for opponent_move in opponent_moves:
                if opponent_move.end_row == king_row and opponent_move.end_col == king_col:
                    appending = False
            if appending:
                legal_moves.append(move)
            self.undo_move()
        return legal_moves
    
    def get_all_moves(self, castling=True):
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
                        self.get_king_moves(r, c, moves, castling)
        return moves
    
    def determine_mate_or_stalemate(self):
        """Function that is called when legal moves is empty"""
        turn = 'w' if self.white_to_move else 'b'
        for r in range(len(self.board)):
            for c in range(len(self.board[0])):
                if self.board[r][c][0] == turn and self.board[r][c][1] == 'K':
                    king_row = r
                    king_col = c
        self.white_to_move = not self.white_to_move
        moves = self.get_all_moves()
        for move in moves:
            if move.end_row == king_row and move.end_col == king_col:
                if self.white_to_move:
                    return "Checkmate, white wins!"
                return "Checkmate, black wins!"
        return "Draw by stalemate"
    def plys_without_captures_or_pawn_moves(self):
        """Returns the number of plys without a pawn move or a capture"""
        plys = 0
        for move in self.log[::-1]:
            if move.piece_moved[1] == "p" or move.piece_captured != "--":
                return plys
            plys += 1
        return plys


    def fen(self):
        "Returns the FEN representation of the board state"
        fen = ""
        empty = 0
        for r in range(len(self.board)):
            for c in range(len(self.board[0])):
                if self.board[r][c] == "--":
                    empty += 1
                else:
                    if empty != 0:  
                        fen += str(empty)
                        empty = 0
                    if self.board[r][c][0] == "w":
                        fen += self.board[r][c][1].upper()
                    else:
                        fen += self.board[r][c][1].lower()
            if empty != 0:
                fen += str(empty)
                empty = 0
            
            if r != 7:
                fen += "/" 
            else:
                fen += " "
        fen += "w " if self.white_to_move else "b " 
        castling_string = ""
        if self.wkc:
            castling_string += "K"
        if self.wqc:
            castling_string += "Q"
        if self.bkc:
            castling_string += "k"
        if self.bqc:
            castling_string += "q"
        
        fen += castling_string if castling_string else "-"
        fen += " "
        
        previous_move = self.log[-1]
        if self.white_to_move:
            if previous_move.piece_moved == "bp" and previous_move.end_row - previous_move.start_row == 2:
                fen += previous_move.get_rank_file(previous_move.end_row - 1, previous_move.end_col)
                fen += " "
            else:
                fen += "- "
        else:
            if previous_move.piece_moved == "wp" and previous_move.end_row - previous_move.start_row == -2:
                fen += previous_move.get_rank_file(previous_move.end_row + 1, previous_move.end_col)
                fen += " "
            else:
                fen += "- "
        fen += str(self.plys_without_captures_or_pawn_moves())
        fen += " "

        fen += str(1 + (len(self.log) // 2))
        return fen
    
    def three_fold_repetition(self):
        if self.position_log[self.fen()[:-4]] == 3:
            return True
        return False

class Move():
    # Conversion from chess notation to indices and reversed
    ranks_to_rows = {"1":7, "2": 6, "3": 5, "4": 4, 
                    "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e":4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, en_passant=False, kc=False, qc=False, pawn_promotion="") -> None:
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.en_passant = en_passant
        self.kc= kc
        self.qc = qc
        self.pawn_promotion = pawn_promotion
        self.move_ID = self.start_row*1000 + self.start_col*100 + self.end_row*10 + self.end_col

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_ID == other.move_ID
        return False

    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + "-" + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]
