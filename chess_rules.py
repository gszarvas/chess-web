import random

# TO DO: 
# Make GitHub Pages playable Website

# Add personalities (balanced, aggressive, defensive) to AI

# Zobrist Hashing 

# (potentially) maintain (row, col) locations for each active piece on the Board

# improve minimax speed by creating Move objects only for Moves it tests 
# i.e. just put start/end pairs into the list 'for move in moves' in minimax
# if in check, skip immediately. only create Move objects for the nodes the AI evaluates
# this removes the need for pseudo_legal_moves and should speed up the AI

# general improvements to evaluate_board 

# give AI opening book e.g. King's Indian Defense, Queen's Pawn, attack the center

PIECE_VALUE = {
    "pawn": 100,
    "knight": 300,
    "bishop": 300,
    "rook": 500,
    "queen": 900,
    "king": 10000
}

DIAGONALS = ((1,1), (1,-1), (-1,1), (-1,-1))
RAYS = ((1,0), (0,1), (-1,0), (0,-1))
KNIGHT_OFFSETS = ((2,1), (1,2), (2,-1), (1, -2), (-2, 1), (-1, 2), (-2, -1), (-1, -2))



class Game:
    def __init__(self):
        self.game_board = Board()
        self.turn = 'white'
        self.move_history = []
        self.game_over = False 
        self.fifty_moves = 0
        
        position = Position(self.game_board, self.turn)
        self.game_board.pos_history[position] = 1

    def switch_turn(self):
        if self.turn == 'white':
            self.turn = 'black'
        else:
            self.turn = 'white'

    def begin_textbased(self):
        print('Welcome to chess! All typical chess rules apply, and white begins the game. The "white" pieces are capitalized,' \
        'and the "black" pieces are not. For each move, enter the square of the piece you would like to move, ' \
        'e.g. a8. Then, a list will be displayed showing all legal destinations of that piece.' \
        'Finally, enter the square you would like to move the piece to, and the game will update the board as necessary.')

        while not self.game_over:
            self.execute_turn(self.turn)
            self.switch_turn()
            if self.game_board.in_check(self.turn):
                print(f"{self.turn.capitalize()} in check!")
            if self.game_board.is_stalemate(self.turn):
                print("Draw by stalemate")
                self.game_over = True
            elif self.game_board.is_checkmate(self.turn):
                self.switch_turn()
                print(f"Checkmate: {self.turn.capitalize()} wins! Game over")
                return 
            elif self.fifty_moves >= 50:
                print("Draw by 50 move rule")
                self.game_over = True  


    def execute_turn(self, turn):
        position = Position(self.game_board, turn)
        for pos in self.pos_history:
            if self.game_board.is_position_same(position, pos):
                self.game_board.pos_history[pos] += 1
                if self.game_board.pos_history[pos] == 3:
                    print("Draw by threefold repetition")
                    self.game_over = True 
                    return 
                break
        else:
            self.pos_history[position] = 1


        print(turn.capitalize() + "\'s turn\n")
        self.game_board.print_board()
        start = str(input("Enter the square of the piece you would like to move.\n "))
        while len(start) != 2 or start[0] not in "abcdefgh" or start[1] not in "12345678":
            print("Error: Invalid square, try again")
            start = str(input("Enter the square of the piece you would like to move.\n "))
        start_row = 8 - int(start[1])
        start_col = ord(start[0]) - ord('a')

        while self.game_board.board[start_row][start_col] is None or self.game_board.board[start_row][start_col].color != turn:
            print("Error: you can't move that!")
            start = str(input("Enter the square of the piece you would like to move.\n "))
            while len(start) != 2 or start[0] not in "abcdefgh" or start[1] not in "12345678":
                print("Error: Invalid square, try again")
                start = str(input("Enter the square of the piece you would like to move.\n "))
            start_row = 8 - int(start[1])
            start_col = ord(start[0]) - ord('a')

        moves = self.game_board.legal_moves(start_row, start_col)

        while len(moves) == 0:
            print("Error: that piece has no legal moves")
            start = str(input("Enter the square of the piece you would like to move.\n "))
            while len(start) != 2 or start[0] not in "abcdefgh" or start[1] not in "12345678":
                print("Error: try again")
                start = str(input("Enter the square of the piece you would like to move.\n "))
            start_row = 8 - int(start[1])
            start_col = ord(start[0]) - ord('a')
            while self.game_board.board[start_row][start_col] is None or self.game_board.board[start_row][start_col].color != turn:
                print("Error: you can't move that!")
                start = str(input("Enter the square of the piece you would like to move.\n "))
                while len(start) != 2 or start[0] not in "abcdefgh" or start[1] not in "12345678":
                    print("Error: Invalid square, try again")
                    start = str(input("Enter the square of the piece you would like to move.\n "))
                start_row = 8 - int(start[1])
                start_col = ord(start[0]) - ord('a')
            moves = self.game_board.legal_moves(start_row, start_col)

        moves_to_display = []

        for move in moves:
            moves_to_display.append(f"{chr(ord('a') + move.end[1])}{8 - move.end[0]}")

        print("Moves:\n")
        print(moves_to_display)
        print()
        
        while True:
            end = str(input(f"Enter the square to which you would like to move the piece on {start}\n"))
            print()
            if len(end) != 2 or end[0] not in 'abcdefgh' or end[1] not in '12345678':
                print("Error: try again")
                continue
            
            end_row, end_col = 8 - int(end[1]), ord(end[0]) - ord('a')

            for move in moves:
                if end_row == move.end[0] and end_col == move.end[1]:
                    if move.is_promotion:
                        print("PROMOTION\n")
                        promo = str(input("Enter the piece type to which you would like to promote, e.g. queen\n"))
                        while promo not in ('queen', 'knight', 'bishop', 'rook'):  # error checking
                            print("Error: try again")
                            promo = str(input("Enter the piece type to which you would like to promote, e.g. queen\n"))
                        move.promotion = promo
                        self.game_board.make_move(move)
                        self.move_history.append(move)
                        return 
                    else:
                        self.game_board.make_move(move)
                        if move.captured is None and move.piece.piece_type != 'pawn':
                            self.fifty_moves += 1
                        else:
                            self.fifty_moves = 0
                        self.move_history.append(move)
                        return 

                else:
                    continue 

            else:
                print("Error: invalid destination square")

        



        
PIECE_TO_CHARACTER = {
    ('pawn', 'black') : 'p',
    ('bishop', 'black') : 'b',
    ('queen', 'black') : 'q',
    ('rook', 'black') : 'r',
    ('knight', 'black') : 'n',
    ('king', 'black') : 'k',
    ('pawn', 'white') : 'P',
    ('bishop', 'white') : 'B',
    ('queen', 'white') : 'Q',
    ('rook', 'white') : 'R',
    ('knight', 'white') : 'N',
    ('king', 'white') : 'K'
}

class Position:
    def __init__(self, board, turn): # using a Board object
        self.turn = turn 
        self.white_castle = board.castle_rights('white') # a list of two booleans referring to [queenside castle, kingside castle] *rights* NOT legality
        self.black_castle = board.castle_rights('black')
        self.passant_square = board.passant_square
    
        self._board_tuple = tuple(
            [None if square is None else (square.piece_type, square.color)
            for row in board.board for square in row]
        )

        self._white_castle_tuple = tuple(self.white_castle)
        self._black_castle_tuple = tuple(self.black_castle)
        
        # Precompute the hash ONCE at creation 
        self._hash = hash((
            self._board_tuple,
            self.turn,
            self._white_castle_tuple,
            self._black_castle_tuple,
            self.passant_square
        ))
            

    def __hash__(self):
        return self._hash

    def __eq__(self, other):
        if not isinstance(other, Position):
            return False 
        if hash(self) != hash(other):
            return False 
        return ( 
            self._board_tuple == other._board_tuple 
            and self.turn == other.turn 
            and self.white_castle == other.white_castle 
            and self.black_castle == other.black_castle 
            and self.passant_square == other.passant_square
        )



class Board:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        for i in range(8):
            self.board[6][i] = Pawn('white')
            self.board[1][i] = Pawn('black')
        self.board[7][3] = Queen('white')
        self.board[0][3] = Queen('black')
        self.board[7][4] = King('white')
        self.board[0][4] = King('black')
        self.board[7][0] = Rook('white')
        self.board[7][7] = Rook('white')
        self.board[0][0] = Rook('black')
        self.board[0][7] = Rook('black')
        self.board[7][1] = Knight('white')
        self.board[7][6] = Knight('white')
        self.board[0][1] = Knight('black')
        self.board[0][6] = Knight('black')
        self.board[7][2] = Bishop('white')
        self.board[7][5] = Bishop('white')
        self.board[0][2] = Bishop('black')
        self.board[0][5] = Bishop('black')
        self.passant = False 
        self.passant_square = None 
        self.white_king_pos = (7, 4)
        self.black_king_pos = (0, 4)
        self.pos_history = {} 
    
    def knight_attacks(self, row, col):
        color = self.board[row][col].color
        possible = [(row + 1, col + 2), (row + 2, col + 1), (row + 2, col - 1), (row + 1, col - 2), 
         (row - 1, col + 2), (row - 2, col + 1), (row - 2, col - 1), (row - 1, col - 2)]
        moves = []
        for r, c in possible:
            if 0 <= r < 8 and 0 <= c < 8:
                if self.board[r][c] is None or self.board[r][c].color != color:
                    moves.append((r, c))
        return moves 
    
    def rook_attacks(self, row, col):
        moves = []
        piece = self.board[row][col]
        r = row
        c = col
        if r < 7:
            r += 1
            square = self.board[r][c]
            while square is None and 0 <= r < 8:
                moves.append((r,c))
                r += 1
                if r > 7:
                    r -= 1
                    break
                square = self.board[r][c]
            if not(square is None) and r < 8 and square.color != piece.color:
                moves.append((r, c))

        r = row
        
        if r > 0:
            r -= 1
            square = self.board[r][c]
            while square is None and 0 <= r < 8:
                moves.append((r, c))
                r -= 1
                if r < 0:
                    r += 1
                    break
                square = self.board[r][c]
            if not(square is None) and r >= 0 and square.color != piece.color:
                moves.append((r, c))
        r = row
        if c < 7:
            c += 1
            square = self.board[r][c]
            while square is None and 0 <= c < 8:
                moves.append((r,c))
                c += 1
                if c > 7:
                    c -= 1
                    break
                square = self.board[r][c]
            if not(square is None) and c < 8 and square.color != piece.color:
                moves.append((r, c))
        c = col
        if c > 0:
            c -= 1
            square = self.board[r][c]
            while square is None and 0 <= c < 8:
                moves.append((r,c))
                c -= 1
                if c < 0:
                    c += 1
                    break
                square = self.board[r][c]
            if not(square is None) and c >= 0 and square.color != piece.color:
                moves.append((r, c))
        return moves
    
    def bishop_attacks(self, row, col):
        moves = []
        piece = self.board[row][col]
        r = row
        c = col 
        if r < 7:
            if c < 7:
                r += 1
                c += 1
                square = self.board[r][c]
                while square is None and 0 <= r < 8 and 0 <= c < 8:
                    moves.append((r,c))
                    r += 1
                    if r > 7:
                        r -= 1
                        break
                    c += 1
                    if c > 7:
                        c -= 1
                        break
                    square = self.board[r][c]
                if not(square is None) and r < 8 and c < 8 and piece.color != square.color:
                    moves.append((r,c))
            r = row
            c = col
            if c > 0:
                r += 1
                c -= 1
                square = self.board[r][c]
                while square is None and 0 <= r < 8 and 0 <= c < 8:
                    moves.append((r,c))
                    r += 1
                    if r > 7:
                        r -= 1
                        break
                    c -= 1
                    if c < 0:
                        c += 1
                        break
                    square = self.board[r][c]
                if not(square is None) and r < 8 and c >= 0 and piece.color != square.color:
                    moves.append((r,c))
        r = row
        c = col
        if r > 0:
            if c < 7:
                r -= 1
                c += 1
                square = self.board[r][c]
                while square is None and 0 <= r < 8 and 0 <= c < 8:
                    moves.append((r,c))
                    r -= 1
                    if r < 0:
                        r += 1
                        break
                    c += 1
                    if c > 7:
                        c -= 1
                        break
                    square = self.board[r][c]
                if not(square is None) and 0 <= r < 8 and c < 8 and piece.color != square.color:
                    moves.append((r,c))
            r = row
            c = col
            if c > 0:
                r -= 1
                c -= 1
                square = self.board[r][c]
                while square is None and 0 <= r < 8 and 0 <= c < 8:
                    moves.append((r,c))
                    r -= 1
                    if r < 0:
                        r += 1
                        break
                    c -= 1
                    if c < 0:
                        c += 1
                        break
                    square = self.board[r][c]
                if not(square is None) and r >= 0 and c >= 0 and piece.color != square.color:
                    moves.append((r,c))
        return moves
    
    def queen_attacks(self, row, col):
        diagonals = self.bishop_attacks(row, col)
        rays = self.rook_attacks(row, col)
        return diagonals + rays
    
    def pawn_moves(self, row, col):
        piece = self.board[row][col]
        moves = []
        r = row
        c = col
        if piece.piece_type == 'pawn':
            if piece.color == 'white':
                # if r == 1:
                #     print("SPECIAL PROMOTION RULES (for white)")   # white is on second row (row 1) and moves up to promote
                #     return
                r -= 1
                square = self.board[r][c]
                if square is None:                                 # white pawn moves up (forward) one square
                    moves.append((r, c))
                                          
                    if piece.has_moved == False:
                        r -= 1
                        square = self.board[r][c]
                        if square is None:         # white pawn can jump two squares on first move
                            moves.append((r,c))

                
            else:
                # if r == 6:
                #     print("SPECIAL PROMOTION RULES (for black)")  # black is on second last row (row 6) and moves down to promote
                #     return
                r += 1
                square = self.board[r][c]
                if square is None:
                    moves.append((r, c))  # black moves down (forward) one square
                    
                    if piece.has_moved == False:
                        r += 1
                        square = self.board[r][c]
                        if square is None: # black can jump two squares on first move
                            moves.append((r,c))
                
        return moves

    def pawn_attacks(self, row, col):
        piece = self.board[row][col] 
        attacks = [] 
        r = row 
        c = col 
        if piece.color == 'white':
            if c < 7:     
                r -= 1
                c += 1
                square = self.board[r][c]
                if not(square is None) and square.color != piece.color:
                    attacks.append((r,c))  # white attacks up and to the right
            c = col 
            r = row 
            if c > 0:
                r -= 1
                c -= 1
                square = self.board[r][c]
                if not(square is None) and square.color != piece.color:
                    attacks.append((r,c)) # white attacks to the left 
        else:
            if c < 7:
                r += 1
                c += 1
                square = self.board[r][c]
                if not(square is None) and square.color != piece.color:
                    attacks.append((r,c))  #  black attacks down and to the right
            c = col 
            r = row
            if c > 0:
                r += 1
                c -= 1
                square = self.board[r][c]
                if square is not None and square.color != piece.color:
                    attacks.append((r,c)) # black attacks down and to the left 
        return attacks 


    
    def king_attacks(self, row, col):
        piece = self.board[row][col]
        attacks = [] 
        possible = [(row + 1, col), (row - 1, col), (row, col + 1,), (row, col - 1), (row + 1, col + 1), (row + 1, col - 1), (row - 1, col - 1), (row - 1, col + 1)]
        for move in possible:
            r1 = move[0]
            c1 = move[1]
            if not(0 <= r1 <= 7) or not(0 <= c1 <= 7):
                continue
            if self.board[r1][c1] is None or self.board[r1][c1].color != piece.color:
                attacks.append(move)
                continue
            
        return attacks





    
    def attacks(self, row, col):  
        piece = self.board[row][col]
        if piece is None:
            return []
        piece_type = piece.piece_type
        if piece_type == 'knight':
            return self.knight_attacks(row, col)
        if piece_type == 'rook':
            return self.rook_attacks(row, col)
        if piece_type == 'bishop':
            return self.bishop_attacks(row, col)
        if piece_type == 'queen':
            return self.queen_attacks(row, col)
        if piece_type == 'pawn':
            return self.pawn_attacks(row, col)  # returns the pawn attacks only
        if piece_type == 'king':
            return self.king_attacks(row, col)
        
    def is_move_legal(self, row, col, move):
        piece = self.board[row][col]           # test move
        target = self.board[move[0]][move[1]]
        self.board[row][col] = None
        self.board[move[0]][move[1]] = piece 
        if piece.piece_type == 'king':
            if piece.color == 'white':
                self.white_king_pos = (move[0], move[1])
            else:
                self.black_king_pos = (move[0], move[1])
        legal = not(self.in_check(piece.color))  # test in_check
        self.board[row][col] = piece             # undo move
        if piece.piece_type == 'king':
            if piece.color == 'white':
                self.white_king_pos = (row, col)
            else:
                self.black_king_pos = (row, col)
        self.board[move[0]][move[1]] = target
        return legal
        
    def legal_moves(self, row, col):  # returns a list of Move objects
        piece = self.board[row][col]
        moves = []
        if piece is None:
            return moves
        possible = self.attacks(row, col) + self.pawn_moves(row,col)  # all attack moves and forward pawn moves
        for move in possible:
            if self.is_move_legal(row, col, move):
                target = self.board[move[0]][move[1]]
                if piece.piece_type == 'pawn':
                    if piece.color == 'white' and row == 1:
                        action = Move(piece, (row, col), move, captured=target, is_promotion = True, promotion = 'queen')
                        moves.append(action)
                        action = Move(piece, (row, col), move, captured=target, is_promotion = True, promotion = 'knight')
                        moves.append(action)
                        action = Move(piece, (row, col), move, captured=target, is_promotion = True, promotion = 'rook')
                        moves.append(action)
                        action = Move(piece, (row, col), move, captured=target, is_promotion = True, promotion = 'bishop')
                        moves.append(action)
                    elif piece.color == 'black' and row == 6:
                        action = Move(piece, (row, col), move, captured=target, is_promotion = True, promotion = 'queen')
                        moves.append(action)
                        action = Move(piece, (row, col), move, captured=target, is_promotion = True, promotion = 'knight')
                        moves.append(action)
                        action = Move(piece, (row, col), move, captured=target, is_promotion = True, promotion = 'rook')
                        moves.append(action)
                        action = Move(piece, (row, col), move, captured=target, is_promotion = True, promotion = 'bishop')
                        moves.append(action)
                    else:
                        action = Move(piece, (row, col), move, captured = target)
                        moves.append(action)
                else:
                    action = Move(piece, (row, col), move, captured=target)
                    moves.append(action)
                

        if piece.piece_type == 'king':
            castle = self.is_castle_legal(piece.color)  # list of 2 booleans referring to queenside (0), kingside (1) castle legality
            if castle[0]:
                action = Move(piece, (row, col), (row, col - 2), is_castle = True)
                moves.append(action)
            if castle[1]:
                action = Move(piece, (row, col), (row, col + 2), is_castle = True)
                moves.append(action)

        if self.passant and piece.piece_type == 'pawn':
            if col < 7:
                right = self.board[row][col + 1] # right neighbor of pawn
                if right is not None and right.piece_type == 'pawn' and right.color != piece.color and (row, col+1) == self.passant_square:
                    if piece.color == 'white':
                        action = Move(piece, (row, col), (row - 1, col + 1), captured = right, is_passant = True)
                        moves.append(action)
                    else:
                        action = Move(piece, (row, col), (row + 1, col + 1), captured = right, is_passant = True)
                        moves.append(action)
            if col > 0:
                left = self.board[row][col - 1] # left neighbor of pawn
                if left is not None and left.piece_type == 'pawn' and left.color != piece.color and (row, col - 1) == self.passant_square:
                    if piece.color == 'white':
                        action = Move(piece, (row, col), (row - 1, col - 1), captured = left, is_passant = True)
                        moves.append(action)
                    else:
                        action = Move(piece, (row, col), (row + 1, col - 1), captured = left, is_passant = True)
                        moves.append(action)
        return moves

    def pseudo_legal_moves(self, row, col):  # returns a list of Move objects
        piece = self.board[row][col]
        moves = []
        if piece is None:
            return moves
        possible = self.attacks(row, col) + self.pawn_moves(row,col)  # all attack moves and forward pawn moves
        for move in possible:
            target = self.board[move[0]][move[1]]
            if piece.piece_type == 'pawn':
                if piece.color == 'white' and row == 1:
                    action = Move(piece, (row, col), move, captured=target, is_promotion = True, promotion = 'queen')
                    moves.append(action)
                    action = Move(piece, (row, col), move, captured=target, is_promotion = True, promotion = 'knight')
                    moves.append(action)
                    action = Move(piece, (row, col), move, captured=target, is_promotion = True, promotion = 'rook')
                    moves.append(action)
                    action = Move(piece, (row, col), move, captured=target, is_promotion = True, promotion = 'bishop')
                    moves.append(action)
                elif piece.color == 'black' and row == 6:
                    action = Move(piece, (row, col), move, captured=target, is_promotion = True, promotion = 'queen')
                    moves.append(action)
                    action = Move(piece, (row, col), move, captured=target, is_promotion = True, promotion = 'knight')
                    moves.append(action)
                    action = Move(piece, (row, col), move, captured=target, is_promotion = True, promotion = 'rook')
                    moves.append(action)
                    action = Move(piece, (row, col), move, captured=target, is_promotion = True, promotion = 'bishop')
                    moves.append(action)
                else:
                    action = Move(piece, (row, col), move, captured = target)
                    moves.append(action)
            else:
                action = Move(piece, (row, col), move, captured=target)
                moves.append(action)
                

        if piece.piece_type == 'king':
            castle = self.is_castle_legal(piece.color)  # list of 2 booleans referring to queenside (0), kingside (1) castle legality
            if castle[0]:
                action = Move(piece, (row, col), (row, col - 2), is_castle = True)
                moves.append(action)
            if castle[1]:
                action = Move(piece, (row, col), (row, col + 2), is_castle = True)
                moves.append(action)

        if self.passant and piece.piece_type == 'pawn':
            if col < 7:
                right = self.board[row][col + 1] # right neighbor of pawn
                if right is not None and right.piece_type == 'pawn' and right.color != piece.color and (row, col+1) == self.passant_square:
                    if piece.color == 'white':
                        action = Move(piece, (row, col), (row - 1, col + 1), captured = right, is_passant = True)
                        moves.append(action)
                    else:
                        action = Move(piece, (row, col), (row + 1, col + 1), captured = right, is_passant = True)
                        moves.append(action)
            if col > 0:
                left = self.board[row][col - 1] # left neighbor of pawn
                if left is not None and left.piece_type == 'pawn' and left.color != piece.color and (row, col - 1) == self.passant_square:
                    if piece.color == 'white':
                        action = Move(piece, (row, col), (row - 1, col - 1), captured = left, is_passant = True)
                        moves.append(action)
                    else:
                        action = Move(piece, (row, col), (row + 1, col - 1), captured = left, is_passant = True)
                        moves.append(action)
        return moves
    
    def make_move(self, move):
        piece = move.piece
        color = move.piece.color

        move.old_passant = self.passant 
        move.old_passant_square = self.passant_square 
        move.old_has_moved = piece.has_moved

        start = move.start  # coordinates of start square
        end = move.end      # coordinates of destination square
        if not(move.is_passant):
            move.captured = self.board[end[0]][end[1]]
        self.board[end[0]][end[1]] = piece  # move piece to destination
        self.board[start[0]][start[1]] = None  # origin becomes empty
        if move.is_passant:
            self.board[start[0]][end[1]] = None  # the enemy pawn is captured behind the official destination square 
        if move.is_castle:
            if end[1] - start[1] > 0:
                rook = self.board[start[0]][7]
                self.board[end[0]][5] = rook 
                self.board[start[0]][7] = None
                rook.has_moved = True
                
            else:
                rook = self.board[start[0]][0]
                self.board[end[0]][3] = rook 
                self.board[start[0]][0] = None
                rook.has_moved = True
            move.piece.is_castled = True 

        if move.piece.piece_type == 'king':
            if color == 'white':
                self.white_king_pos = (end[0], end[1])
            else:
                self.black_king_pos = (end[0], end[1])

        if move.is_promotion:
            if move.promotion == 'queen':
                self.board[end[0]][end[1]] = Queen(piece.color)
            if move.promotion == 'knight':
                self.board[end[0]][end[1]] = Knight(piece.color)
            if move.promotion == 'bishop':
                self.board[end[0]][end[1]] = Bishop(piece.color)
            if move.promotion == 'rook':
                self.board[end[0]][end[1]] = Rook(piece.color)

        piece.has_moved = True  
         
        if piece.piece_type == 'pawn' and abs(end[0] - start[0]) == 2:
            self.passant = True 
            self.passant_square = (end[0], end[1])
        else: 
            self.passant = False 
            self.passant_square = None 

    def undo_move(self, move):
        color = move.piece.color
        if move.is_castle:
            if move.end[1] - move.start[1] > 0:  # move was a kingside castle
                self.board[move.start[0]][move.start[1]] = move.piece
                self.board[move.end[0]][move.end[1]] = None 
                
                self.board[move.start[0]][7] = self.board[move.start[0]][5]
                self.board[move.start[0]][5] = None 
                self.board[move.start[0]][7].has_moved = False 
                
            else:  # move was a queenside castle
                self.board[move.start[0]][move.start[1]] = move.piece  # move king back
                self.board[move.end[0]][move.end[1]] = None 
                 
                self.board[move.start[0]][0] = self.board[move.start[0]][3] # move rook back
                self.board[move.start[0]][3] = None 
                self.board[move.start[0]][0].has_moved = False
            move.piece.is_castled = False 
            
        elif move.is_passant:
            if move.piece.color == 'white':
                self.board[move.start[0]][move.end[1]] = move.captured  # put the captured pawn back
                if move.captured is not None:
                    move.captured.has_moved = True  # reset has_moved for the pawn that was captured
                self.board[move.start[0]][move.start[1]] = move.piece  # put moved pawn back
                self.board[move.end[0]][move.end[1]] = None  
            elif move.piece.color == 'black':
                self.board[move.start[0]][move.end[1]] = move.captured  # put the captured pawn back
                if move.captured is not None:
                    move.captured.has_moved = True  # reset has_moved
                self.board[move.start[0]][move.start[1]] = move.piece  # put moved pawn back
                self.board[move.end[0]][move.end[1]] = None
            
        else: # also handles undoing promotions because move.captured replaces the promotion
            self.board[move.start[0]][move.start[1]] = move.piece
            self.board[move.end[0]][move.end[1]] = move.captured
        if move.piece.piece_type == 'king':
            if color == 'white':
                self.white_king_pos = (move.start[0], move.start[1])
            else:
                self.black_king_pos = (move.start[0], move.start[1])

        self.passant = move.old_passant 
        self.passant_square = move.old_passant_square
        move.piece.has_moved = move.old_has_moved
        return 
    
    def get_all_moves(self, color):
        moves = []
        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                if piece is not None and piece.color == color:
                    moves.extend(self.legal_moves(i, j)) 
        return moves 

    def get_all_pseudo_moves(self, color):
            moves = []
            for i in range(8):
                for j in range(8):
                    piece = self.board[i][j]
                    if piece is not None and piece.color == color:
                        moves.extend(self.pseudo_legal_moves(i, j)) 
            return moves 


        


    def print_board(self):  # ascii style board print
        print("BOARD:")
        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                if piece is None:
                    print("  ", end=' ')
                else:
                    if piece.piece_type == 'knight':
                        if piece.color == 'white':
                            print(' N ', end = '')
                        else:
                            print(' n ', end = '')
                    elif piece.color == 'white':
                        print(' ' + piece.piece_type.capitalize()[0], end = ' ')
                    else:
                        print(' '+ piece.piece_type[0], end = ' ')
                if j == 7:
                    print(f"    {8 - i}")
        print()
        print(" a  b  c  d  e  f  g  h ")
    
    def in_check(self, color): # checks if the king of the input color is in check
        king_pos = self.white_king_pos if color == 'white' else self.black_king_pos
        if color == 'white': # check for pawn attacks, black pawns attack the king from above (decrement row to check)
            row, col = king_pos[0] - 1, king_pos[1] + 1  # possible pawn attacker to the right
            if 0 <= row < 8 and 0 <= col < 8:
                piece = self.board[row][col]
                if piece is not None and piece.color != color and piece.piece_type == 'pawn':
                    return True 
                
            row, col = row, col - 2  # possible pawn attacker to the left
            if 0 <= row < 8 and 0 <= col < 8:
                piece = self.board[row][col]
                if piece is not None and piece.color != color and piece.piece_type == 'pawn':
                    return True 
            
        else: # check for pawn attacks, white pawns attack the king from below (increment row to check)
            row, col = king_pos[0] + 1, king_pos[1] + 1  # possible pawn attacker to the right
            if 0 <= row < 8 and 0 <= col < 8:
                piece = self.board[row][col]
                if piece is not None and piece.color != color and piece.piece_type == 'pawn':
                    return True 
                
            row, col = row, col - 2  # possible pawn attacker to the left
            if 0 <= row < 8 and 0 <= col < 8:
                piece = self.board[row][col]
                if piece is not None and piece.color != color and piece.piece_type == 'pawn':
                    return True

        for dr, dc in KNIGHT_OFFSETS: # check for knight attacks
            row, col = king_pos[0] + dr, king_pos[1] + dc 
            if 0 <= row < 8 and 0 <= col < 8:
                piece = self.board[row][col]
                if piece is not None and piece.color != color and piece.piece_type == 'knight':
                    return True

        for dr, dc in DIAGONALS: # check for bishop and queen attacks
            row, col = king_pos[0] + dr, king_pos[1] + dc 
            distance = 1
            while 0 <= row < 8 and 0 <= col < 8:
                piece = self.board[row][col]
                if piece is not None:
                    if piece.color != color and piece.piece_type in ('bishop', 'queen'):
                        return True
                    elif piece.piece_type == 'king':
                        if distance == 1:
                            return True 
                    break
                row += dr 
                col += dc 
                distance += 1

        for dr, dc in RAYS: # check for rook and queen attacks
            row, col = king_pos[0] + dr, king_pos[1] + dc 
            distance = 1
            while 0 <= row < 8 and 0 <= col < 8:
                piece = self.board[row][col]
                if piece is not None:
                    if piece.color != color and piece.piece_type in ('rook', 'queen'):
                        return True
                    elif piece.color != color and piece.piece_type == 'king':
                        if distance == 1:
                            return True
                    break 
                row += dr 
                col += dc
                distance += 1

        return False  
            
        # king_pos = self.white_king_pos if color == 'white' else self.black_king_pos  
        # return self.is_square_attacked(king_pos, color)
    
    def is_square_attacked(self, square, color):
        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                if piece is None or piece.color == color:
                    continue
                else:
                    if piece.piece_type == 'knight':
                        dr = abs(square[0] - i)
                        dc = abs(square[1] - j)
                        if (dr == 2 and dc == 1) or (dr == 1 and dc == 2):
                            return True 
                    if piece.piece_type == 'king':
                        dr = abs(square[0] - i)
                        dc = abs(square[1] - j)
                        if max(dr, dc) == 1:
                            return True 
                    if piece.piece_type == 'rook':
                        if i == square[0]: # rook on same row
                            if j < square[1]:
                                for col in range(j+1, square[1]):
                                    if self.board[i][col] is not None:
                                        break
                                else:
                                    return True 
                            else:
                                for col in range(j-1, square[1], -1):
                                    if self.board[i][col] is not None:
                                        break 
                                else:
                                    return True
                                
                        elif j == square[1]: # rook on same col
                            if i < square[0]:
                                for row in range(i+1, square[0]):
                                    if self.board[row][j] is not None:
                                        break
                                else:
                                    return True 
                            else:
                                for row in range(i-1, square[0], -1):
                                    if self.board[row][j] is not None:
                                        break 
                                else:
                                    return True 

                    if piece.piece_type == 'bishop':
                        if i+j == square[0] + square[1] or i-j == square[0] - square[1]:
                            dr = 1 if square[0] > i else -1
                            dc = 1 if square[1] > j else -1
                            row = i + dr 
                            col = j + dc 
                            while (row, col) != square:
                                if self.board[row][col] is not None:
                                    break
                                row += dr 
                                col += dc 
                            else:
                                return True 
                        
                    if piece.piece_type == 'pawn':
                        attacks = self.pawn_attacks(i, j)
                        if square in attacks:
                            return True 
                         
                    if piece.piece_type == 'queen':
                        if i+j == square[0] + square[1] or i-j == square[0] - square[1]: # diagonals check (like bishop)
                            dr = 1 if square[0] > i else -1
                            dc = 1 if square[1] > j else -1
                            row = i + dr 
                            col = j + dc 
                            while (row, col) != square:
                                if self.board[row][col] is not None:
                                    break
                                row += dr 
                                col += dc 
                            else: 
                                return True 
                        
                        elif i == square[0]: # rays check (like rook)
                            if j < square[1]:
                                for col in range(j+1, square[1]):
                                    if self.board[i][col] is not None:
                                        break
                                else:
                                    return True 
                            else:
                                for col in range(j-1, square[1], -1):
                                    if self.board[i][col] is not None:
                                        break 
                                else:
                                    return True
                                
                        elif j == square[1]: # rook on same col
                            if i < square[0]:
                                for row in range(i+1, square[0]):
                                    if self.board[row][j] is not None:
                                        break
                                else:
                                    return True 
                            else:
                                for row in range(i-1, square[0], -1):
                                    if self.board[row][j] is not None:
                                        break 
                                else:
                                    return True
        return False 
    
    def is_castle_legal(self, color): # returns a list of 2 bools [T/F, T/F] referring to (queenside, kingside) castle legality
        bool_list = [False, False]
        if self.in_check(color):
            return bool_list
        if color == 'black':
            if (self.board[0][4] is None or self.board[0][4].piece_type != 'king'):  # black king is not on home square
                return bool_list 
            king = self.board[0][4]
            if king.has_moved:
                return bool_list
            if self.board[0][1] is None and self.board[0][2] is None and self.board[0][3] is None: # queenside is empty
                if self.board[0][0] is None or self.board[0][0].piece_type != 'rook' or self.board[0][0].has_moved:  # black, non-moved, queenside rook is NOT on home square
                    bool_list[0] = False 
                else: # black, non-moved, queenside rook IS on home square
                    if not(self.is_square_attacked((0,2), 'black') or self.is_square_attacked((0,3), 'black')):
                        bool_list[0] = True
                    else: 
                        bool_list[0] = False 
            else: # queenside is not empty
                bool_list[0] = False
            if self.board[0][5] is None and self.board[0][6] is None: # kingside is empty
                if self.board[0][7] is None or self.board[0][7].piece_type != 'rook' or self.board[0][7].has_moved: # black, non-moved, kingside rook is NOT on home square
                    bool_list[1] = False
                else: # black, non-moved, kingside rook IS on home square
                    if not(self.is_square_attacked((0,5), 'black') or self.is_square_attacked((0,6), 'black')):
                        bool_list[1] = True
                    else: 
                        bool_list[1] = False 
            else: # else kingside is not empty
                bool_list[1] = False 

        if color == 'white':
            if (self.board[7][4] is None or self.board[7][4].piece_type != 'king'):  # white king is not on home square
                return bool_list
            king = self.board[7][4]
            if king.has_moved:
                return bool_list  
            if self.board[7][1] is None and self.board[7][2] is None and self.board[7][3] is None: # queenside is empty
                if self.board[7][0] is None or self.board[7][0].piece_type != 'rook' or self.board[7][0].has_moved:  # white, non-moved, queenside rook is NOT on home square
                    bool_list[0] = False 
                else: # white, non-moved, queenside rook IS on home square
                    if not(self.is_square_attacked((7,2), 'white') or self.is_square_attacked((7,3), 'white')):
                        bool_list[0] = True
                    else: 
                        bool_list[0] = False  
            else: # queenside is not empty
                bool_list[0] = False
            if self.board[7][5] is None and self.board[7][6] is None: # kingside is empty
                if self.board[7][7] is None or self.board[7][7].piece_type != 'rook' or self.board[7][7].has_moved: # white, non-moved, kingside rook is NOT on home square
                    bool_list[1] = False
                else: # white, non-moved, kingside rook IS on home square
                    if not(self.is_square_attacked((7,5), 'white') or self.is_square_attacked((7,6), 'white')):
                        bool_list[1] = True
                    else: 
                        bool_list[1] = False 
            else: # else kingside is not empty
                bool_list[1] = False
        
        return bool_list 
    
    def castle_rights(self, color):
        castle_rights = [False, False]  # refers to [queenside, kingside] castle legality

        if color == 'white':
            rook1 = self.board[7][0]
            king = self.board[7][4]
            rook2 = self.board[7][7]
            if (not(rook1 is None) and not(king is None)):
                if rook1.piece_type == 'rook' and king.piece_type == 'king' and rook1.has_moved == False and king.has_moved == False:
                    castle_rights[0] = True
            elif (not(king is None) and not(rook2 is None)):
                if rook2.piece_type == 'rook' and king.piece_type == 'king' and rook2.has_moved == False and king.has_moved == False:
                    castle_rights[1] = True
        if color == 'black':
            rook1 = self.board[0][0]
            king = self.board[0][4]
            rook2 = self.board[0][7]
            if (not(rook1 is None) and not(king is None)):
                if rook1.piece_type == 'rook' and king.piece_type == 'king' and rook1.has_moved == False and king.has_moved == False:
                    castle_rights[0] = True
            elif (not(king is None) and not(rook2 is None)):
                if rook2.piece_type == 'rook' and king.piece_type == 'king' and rook2.has_moved == False and king.has_moved == False:
                    castle_rights[1] = True

        return castle_rights 

    
    def is_stalemate(self, color):  # checks if the given color is in stalemate
        move_counter = 0
        for i in range(8):
            for j in range(8):
                if not(self.board[i][j] is None) and self.board[i][j].color == color:
                    moves = self.legal_moves(i, j)
                    move_counter = move_counter + len(moves)
        if move_counter == 0 and not(self.in_check(color)):
            return True
        return False 
    
    def is_checkmate(self, color): # likewise ^^
        move_counter = 0
        for i in range(8):
            for j in range(8):
                if not(self.board[i][j] is None) and self.board[i][j].color == color:
                    moves = self.legal_moves(i, j)
                    move_counter = move_counter + len(moves)
        if move_counter == 0 and self.in_check(color):
            return True
        return False
    
    def is_position_same(self, pos1, pos2):
        return ( 
            pos1.board_state == pos2.board_state 
            and pos1.turn == pos2.turn 
            and pos1.white_castle == pos2.white_castle 
            and pos1.black_castle == pos2.black_castle 
            and pos1.passant_square == pos2.passant_square
        )
        


class Move:
    def __init__(self, piece, start, end, captured = None, is_castle = False, is_passant = False, 
                 old_passant = False, old_passant_square = None, old_has_moved = False, is_promotion = False, promotion = None):
        self.piece = piece 
        self.start = start  # tuple (row, col)
        self.end = end  # tuple (row, col)
        self.captured = captured
        self.is_castle = is_castle
        self.is_passant = is_passant 
        self.is_promotion = is_promotion
        self.promotion = promotion
        self.old_passant = old_passant                  # these three are useful for undo_move
        self.old_passant_square = old_passant_square    #
        self.old_has_moved = old_has_moved              #
        self.priority = self.priority()
        self.key = (piece.piece_type, start, end, promotion)

    def __eq__(self, other):
        if not isinstance(other, Move):
            return NotImplemented

        if (self.start != other.start) or (self.end != other.end):
            return False 

        return (
            self.piece.piece_type == other.piece.piece_type
            and self.promotion == other.promotion
        )


    def priority(self):
        priority = 0
        
        if self.captured is not None:
            priority += (
                10 * (PIECE_VALUE[self.captured.piece_type]) - PIECE_VALUE[self.piece.piece_type]
            )
        if self.is_castle:
            priority += 100 
        if self.is_promotion:
            priority += 10000

        return priority 




class Pawn:
    def __init__(self, color):
        self.color = color
        self.has_moved = False
        self.piece_type = 'pawn'
class Knight:
    def __init__(self, color):
        self.color = color
        self.piece_type = 'knight'
        self.has_moved = False
class Bishop:
    def __init__(self, color):
        self.color = color
        self.piece_type = 'bishop'
        self.has_moved = False 
class Rook:
    def __init__(self, color):
        self.color = color
        self.has_moved = False
        self.piece_type = 'rook'
class Queen:
    def __init__(self, color):
        self.color = color
        self.piece_type = 'queen'
        self.has_moved = False 
class King:
    def __init__(self, color):
        self.color = color
        self.has_moved = False
        self.piece_type = 'king'
        self.is_castled = False 

if __name__ == "__main__":
    move1 = Move(Knight('white'), (1,1), (2,3), None, False, False)
    move2 = Move(Knight('black'), move1.start, move1.end, move1.captured)
    print(move1 == move2)

#     board = Board()
#     turn = 'white'

#     for _ in range(30):
#         all_moves = []

#         for row in range(8):
#             for col in range(8):
#                 piece = board.board[row][col]
#                 if piece is not None and piece.color == turn:
#                     all_moves.extend(board.legal_moves(row, col))

#         if not all_moves:
#             break

#         move = random.choice(all_moves)
#         board.make_move(move)
#         turn = "black" if turn == "white" else "white"
    
#     num_tests = 0

#     for row in range(8):
#         for col in range(8):
#             for move in board.legal_moves(row, col):
#                 position_before = Position(board, turn)

#                 board.make_move(move)
#                 board.undo_move(move)

#                 position_after = Position(board, turn)

#                 assert position_before == position_after
#                 assert board.passant == move.old_passant
#                 assert board.passant_square == move.old_passant_square

#                 num_tests += 1

#     print(f"Passed {num_tests} undo tests!")

