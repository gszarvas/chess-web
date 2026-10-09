import random
import pickle 
import os 
from chess_rules import Position
from chess_rules import ZOBRIST_PIECES, ZOBRIST_TURN, ZOBRIST_CASTLING, ZOBRIST_EN_PASSANT 
from chess_rules import Move 
from chess_rules import WHITE, BLACK 

TT_EXACT = 0
TT_LOWERBOUND = 1
TT_UPPERBOUND = 2

DEFENSIVE = 0  # for bot personalities
BALANCED = 1   #
AGGRESSIVE = 2 #

# Point values are currently 1.5x original values e.g. 100, 320, 330, 500, 900
POINT_VALUES = { 
            (0, BLACK) : -150,
            (2, BLACK) : -495,
            (4, BLACK) : -1350,
            (3, BLACK) : -750,
            (1, BLACK) : -480,
            (0, WHITE) : 150,
            (2, WHITE) : 495,
            (4, WHITE) : 1350,
            (3, WHITE) : 750,
            (1, WHITE) : 480
            }

POSITION_SCORES = (
    # pawn position scores (these are for white. for black, swap for the correct row, i.e. (7 - row) )
    ( 0,  0,  0,  0,  0,  0,  0,  0,
     50, 50, 50, 50, 50, 50, 50, 50,
     30, 30, 30, 30, 30, 30, 30, 30,
     10, 16, 16, 25, 25, 16, 16, 10,
      0,  6, 12, 25, 25, 12,  6,  0,
      3,  0,  4, 10, 10,  4,  0,  3,
      6,  6,  4, -1, -1,  4,  6,  6,
      0,  0,  0,  0,  0,  0,  0,  0 
     ), 
     # knight position scores  (currently symmetric about the center, so white/black does not matter)
    (-20, -10, -10, -10, -10, -10, -10, -20,
     -10,  -7,  -7,   1,   1,  -7,  -7, -10,
      -7,   5,  20,  15,  15,  20,   5,  -7,
      -7,  10,  15,  15,  15,  15,  10,  -7,
      -7,  10,  15,  15,  15,  15,  10,  -7, 
      -7,   5,  20,  15,  15,  20,  5,   -7,
      -10,  -7,  -7,   1,   1,  -7,  -7, -10,
      -20, -10, -10, -10, -10, -10, -10, -20
     ),
     # bishop position scores (centrally symmetric)
    (  5,   0,  -5,  -5,  -5,  -5,   0,   5,
     -10,  20,   0,   3,   3,   0,  20, -10,
      -5,   5,  15,   0,   0,  15,   5,  -5,
      -7,  10,  15,   5,   5,  15,  10,  -7,
      -7,  10,  15,   5,   5,  15,  10,  -7, 
      -5,   5,  15,   0,   0,  15,   5,  -5,
     -10,  20,   0,   3,   3,   0,  20, -10,
       5,   0,  -5,  -5,  -5,  -5,   0,   5
     ),
     # rook position scores (centrally symmetric)
    (  0,  0,  8, 12, 12,  8,  0,  0,
       5,  5, 13, 15, 15, 13,  5,  5,
       2,  2, 10,  8,  8, 10,  2,  2,
       2,  2,  8,  6,  6,  8,  2,  2,
       2,  2,  8,  6,  6,  8,  2,  2,
       2,  2, 10,  8,  8, 10,  2,  2,
       5,  5, 13, 15, 15, 13,  5,  5,
       0,  0,  8, 12, 12,  8,  0,  0
     ),
     # queen position scores (centrally symmetric)
    (  0,  0,  8, 12, 12,  8,  0,  0,
       5,  5, 15, 16, 16, 15,  5,  5,
       3,  6,  5,  5,  5,  5,  6,  3,
       3,  3,  5,  6,  6,  5,  3,  3,
       3,  3,  5,  6,  6,  5,  3,  3,
       3,  6,  5,  5,  5,  5,  6,  3,
       5,  5, 15, 16, 16, 15,  5,  5,
       0,  0,  8, 12, 12,  8,  0,  0
     ),
     # king position scores   # rewards safe king, need separate eval for endgame king
    (  5, 10, 15,  0,  8,  2, 15,  5,
       0,  3,  0,  0,  0,  0,  3,  0,
       1,  1,  2,  2,  2,  2,  1,  1,
       1,  1,  2,  3,  3,  2,  1,  1,
       1,  1,  2,  3,  3,  2,  1,  1,
       1,  1,  2,  2,  2,  2,  1,  1,
       0,  3,  0,  0,  0,  0,  3,  0,
       5, 10, 15,  0,  8,  2, 15,  5
     ),
)


class Opponent:
    def __init__(self, difficulty = None, color = BLACK):
        self.difficulty = difficulty 
        self.color = color 
        self.cutoffs = 0
        self.evaluations = 0
        self.transposition_table = {}
        # self.load_tt()
        self.killer_moves = [[None, None, None] for _ in range(10)]  # choose max_depth + 1 ####
        self.tt_order_hits = 0

    def load_tt(self):
        if os.path.exists("transposition_table.pkl"):
            with open("transposition_table.pkl", "rb") as f:
                self.transposition_table = pickle.load(f)
        else:
            self.transposition_table = {}


    def save_tt(self):
        good_entries = {
            key: entry
            for key, entry in self.transposition_table.items()
            if entry["depth"] >= 5
        }
        with open("transposition_table.pkl", "wb") as f:
            pickle.dump(good_entries, f)
        return

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty

    def set_color(self, color):
        self.color = color

    def choose_move(self, board):  # a board object
        if self.difficulty == 0:
            return random.choice(board.get_all_moves(self.color))
        else:
            best_move = None
            for d in range(1, self.difficulty + 1):
                score, move = self.minimax(board, d, self.color, -float('inf'), float('inf'))
                best_move = move
            print(score, best_move.key)
            return best_move
            # score, move = self.minimax(board, self.difficulty, self.color, -float('inf'), float('inf'))
            # return move

    def eval_king_pos(self, king, king_pos): # pass the King object and king_pos tuple 
        bonus = 0
        i = king_pos[0] # row
        j = king_pos[1] # col 
        if 2 < j < 5:
            bonus -= 20
        if king.has_moved and not(king.is_castled):
            bonus -= 10
        if king.is_castled:
            bonus += 50

        return bonus 

         
    def evaluate_board(self, board):  # a board object
        score = 0

        # wking = board.board[board.white_king_pos[0]][board.white_king_pos[1]] # safe lookup because king always exists on board
        # bking = board.board[board.black_king_pos[0]][board.black_king_pos[1]]
        for i in range(8):  # rook/queen x-raying bonus (early/basic version)
            piece = board.board[i][board.white_king_pos[1]]
            if piece is not None and (piece.piece_type == 3 or piece.piece_type == 4) and piece.color == BLACK:
                score -= 30
            piece = board.board[i][board.black_king_pos[1]]
            if piece is not None and (piece.piece_type == 3 or piece.piece_type == 4) and piece.color == WHITE:
                score += 30
        # score += self.eval_king_pos(wking, board.white_king_pos) # add king bonus (positive for white)
        # score -= self.eval_king_pos(bking, board.black_king_pos) # subtract king bonus (negative for black)

        for piece in board.pieces:
            if piece.position is None:
                continue 

            if piece.piece_type != 5:
                score += POINT_VALUES[(piece.piece_type, piece.color)]

            i, j = piece.position
            square = 8 * i + j 
            if piece.piece_type == 0:
                if piece.color == WHITE:
                    score += POSITION_SCORES[0][square]
                    if piece.has_moved and board.black_king_pos[1] - 1 <= j <= board.black_king_pos[1] + 1:
                        score += 3 * i
                else:
                    score -= POSITION_SCORES[0][8*(7-i) + j]
                    if piece.has_moved and board.white_king_pos[1] - 1 <= j <= board.white_king_pos[1] + 1:
                        score -= 3 * (7 - i)
                continue 

            if board.captures <= 11 and piece.piece_type == 4:  # basically an early game detector for queen moves
                # minor penalty for too early queen development
                if piece.has_moved:
                    score -= piece.color * 20
                continue 

            if piece.color == WHITE:
                score += POSITION_SCORES[piece.piece_type][square]
                if piece.has_moved:
                    score += 5
            else:
                score -= POSITION_SCORES[piece.piece_type][square]
                if piece.has_moved:
                    score -= 5

        return score 

    def minimax(self, board, depth, color, alpha, beta, ply = 0, zobrist_hash = None):  # ply useful for killer moves 
        alpha_orig = alpha 
        beta_orig = beta 
        black_castle = tuple(board.black_castle)  # needed for update_zobrist (specific enemy castle rights edge case)
        white_castle = tuple(board.white_castle) 
        if depth == 0:
            self.evaluations += 1
            return self.evaluate_board(board), None  # return score, move 
        if zobrist_hash is None:
            zobrist_hash = Position(board, color).calculate_zobrist_hash()
        if board.pos_history.get(zobrist_hash, 0) == 3:
            return 0, None

        # pos = Position(board, color, zobrist_hash)
        preferred_move = None 
        entry = self.transposition_table.get(zobrist_hash)
        if entry is not None:
            preferred_move = entry.get('move')  # a move key
            move = board.key_to_move(preferred_move)
            
            board.make_move(move)   # first check for threefold repetition
            new_black_castle = tuple(board.black_castle)  
            new_white_castle = tuple(board.white_castle) 
            if color == WHITE:
                new_zobrist_hash = self.update_zobrist_hash(zobrist_hash, move, white_castle, black_castle)
            else:
                new_zobrist_hash = self.update_zobrist_hash(zobrist_hash, move, black_castle, white_castle)
            board.pos_history[new_zobrist_hash] = board.pos_history.get(new_zobrist_hash, 0) + 1
            if board.pos_history[new_zobrist_hash] == 3:  # if threefold, get rid of tt move and let search happen normally
                # print("Entered threefold detection in TT")
                board.undo_move(move)
                board.pos_history[new_zobrist_hash] -= 1
                if board.pos_history[new_zobrist_hash] == 0:
                    del board.pos_history[new_zobrist_hash]
                move = None 
            else: # it is not immediate threefold 
                opp = WHITE if color == BLACK else BLACK
                moves = board.get_all_moves(opp)
                for action in moves:
                    if opp == WHITE:
                        reply_hash = self.update_zobrist_hash(new_zobrist_hash, action, new_white_castle, new_black_castle)
                    else:
                        reply_hash = self.update_zobrist_hash(new_zobrist_hash, action, new_black_castle, new_white_castle)
                    if board.pos_history.get(reply_hash, 0) == 2:  # opponent can choose a drawing move
                        board.undo_move(move)
                        board.pos_history[new_zobrist_hash] -= 1
                        if board.pos_history[new_zobrist_hash] == 0:
                            del board.pos_history[new_zobrist_hash]
                        move = None 
                        break 
                if move is not None:
                    board.undo_move(move)
                    board.pos_history[new_zobrist_hash] -= 1
                    if board.pos_history[new_zobrist_hash] == 0:
                        del board.pos_history[new_zobrist_hash]


            if move is not None and entry['depth'] >= depth:
                tt_score = entry['score']
                tt_flag = entry['flag']
                if tt_flag == TT_EXACT:
                    return tt_score, move
                elif tt_flag == TT_LOWERBOUND:
                    alpha = max(alpha, tt_score)
                elif tt_flag == TT_UPPERBOUND:
                    beta = min(beta, tt_score)
                
                if alpha >= beta:
                    self.tt_order_hits += 1
                    return tt_score, move
        
        moves = board.get_all_pseudo_moves(color)
        # for move in moves:
        #     print(move.key, move.priority, depth, color)
        num_white_moves = 0
        num_black_moves = 0
                
        killers = self.killer_moves[ply] if ply < len(self.killer_moves) else [None, None, None]  ####
        moves.sort(
            key=lambda move: self.move_order_score(move, preferred_move, killers), 
            reverse=True
        )
                
        if color == WHITE:
            best_score = -float('inf')
            best_move = None 
            
            for move in moves:

                board.make_move(move)
                if board.in_check(WHITE):
                    board.undo_move(move)
                    continue 
                
                new_zobrist_hash = self.update_zobrist_hash(zobrist_hash, move, white_castle, black_castle)

                num_white_moves += 1
                
                board.pos_history[new_zobrist_hash] = board.pos_history.get(new_zobrist_hash, 0) + 1
                if board.pos_history[new_zobrist_hash] == 3:
                    score = 0
                    # print("Set score to 0 (white)")
                else: 
                    score, _ = self.minimax(board, depth - 1, BLACK, alpha, beta, ply + 1, new_zobrist_hash)

                board.pos_history[new_zobrist_hash] -= 1
                if board.pos_history[new_zobrist_hash] == 0:
                    del board.pos_history[new_zobrist_hash]

                board.undo_move(move) 
                
                if score > best_score:
                    best_score = score 
                    best_move = move 
                # print("Best score (white):", best_score)
                alpha = max(alpha, best_score)
                if alpha >= beta:
                    self.cutoffs += 1
                    if move.captured is None and not move.is_promotion: 
                        self.add_killer_move(ply, move)
                    break 
            if num_white_moves == 0:
                if board.in_check(WHITE):
                    return -1000000 + ply, None
                else:
                    return 0, None 

        else: # color is black
            best_score = float('inf') 
            best_move = None 
            for move in moves:
                board.make_move(move)
                if board.in_check(BLACK):
                    board.undo_move(move)
                    continue 
                 
                new_zobrist_hash = self.update_zobrist_hash(zobrist_hash, move, black_castle, white_castle)

                num_black_moves += 1
                
                board.pos_history[new_zobrist_hash] = board.pos_history.get(new_zobrist_hash, 0) + 1
                if board.pos_history[new_zobrist_hash] == 3:
                    score = 0
                    # print("Set score to 0 (black)")
                else:
                    score, _ = self.minimax(board, depth - 1, WHITE, alpha, beta, ply + 1, new_zobrist_hash)

                board.pos_history[new_zobrist_hash] -= 1
                if board.pos_history[new_zobrist_hash] == 0:
                    del board.pos_history[new_zobrist_hash]

                board.undo_move(move) 
                if score < best_score:
                    best_score = score 
                    best_move = move 
                # print("Best score (black):", best_score)
                beta = min(beta, best_score)
                if alpha >= beta:
                    self.cutoffs += 1
                    if move.captured is None and not move.is_promotion: 
                        self.add_killer_move(ply, move)
                    break
                # if depth == 4:
                #     print("Candidates: (black)")
                #     print(move.start, move.end, score)
                #     print()
            if num_black_moves == 0:
                if board.in_check(BLACK):
                    return 1000000 - ply, None 
                else:
                    return 0, None 


        if color == WHITE:
            if best_score <= alpha_orig:
                flag = TT_UPPERBOUND
            elif best_score >= beta_orig:
                flag = TT_LOWERBOUND
            else:
                flag = TT_EXACT
        else:
            if best_score >= alpha_orig:
                flag = TT_LOWERBOUND
            elif best_score <= beta_orig:
                flag = TT_UPPERBOUND
            else:
                flag = TT_EXACT

        self.transposition_table[zobrist_hash] = {
            'depth' : depth,
            'score' : best_score,
            'move' : best_move.key if best_move is not None else None,
            'flag' : flag
        }
        return best_score, best_move

    def move_order_score(self, move, preferred, killers):  # preferred is a key and killers contains keys
        score = move.priority
        if preferred is not None and move.key == preferred:
            # print("TT move gets priority")
            score += 1000000
        if killers[0] is not None and move.key == killers[0]:
            # print("Killer[0] gets priority")
            score += 9000
        if killers[1] is not None and move.key == killers[1]:
            # print("Killer[1]")
            score += 8000
        if killers[2] is not None and move.key == killers[2]:
            # print("Killer[2]")
            score += 7000
        return score 

    def add_killer_move(self, ply, move):
        if ply >= len(self.killer_moves):
            return
        killers = self.killer_moves[ply]

        if move.key in killers:
            return 
        killers.insert(0, move.key)
        if len(killers) > 3:
            killers.pop()

    def update_zobrist_hash(self, zobrist_hash, move, friendly_castling, enemy_castling): # expects a zobrist_hash and a Move object, and friendly and enemy castling boolean 2-tuples

        start_row, start_col = move.start
        end_row, end_col = move.end

        start_square = start_row * 8 + start_col
        end_square = end_row * 8 + end_col 

        piece = move.piece 
        color = piece.color
        piece_type = move.key[0]
        captured_type = move.captured_type

        if move.is_promotion:
            zobrist_hash ^= ZOBRIST_PIECES[(0, color, start_square)]
            zobrist_hash ^= ZOBRIST_PIECES[(move.promotion, color, end_square)]
        else:
            zobrist_hash ^= ZOBRIST_PIECES[(piece_type, color, start_square)]
            zobrist_hash ^= ZOBRIST_PIECES[(piece_type, color, end_square)]

        if move.captured is not None:
            captured_color = move.captured.color
            if move.is_passant:
                captured_square = start_row * 8 + end_col 
            else:
                captured_square = end_square 
            zobrist_hash ^= ZOBRIST_PIECES[(captured_type, captured_color, captured_square)]

        zobrist_hash ^= ZOBRIST_TURN 
        if move.old_passant_square is not None:
            row, col = move.old_passant_square
            square = row * 8 + col 
            zobrist_hash ^= ZOBRIST_EN_PASSANT[square]
        if piece_type == 0 and abs(end_row - start_row) == 2:
            square = end_row * 8 + end_col
            zobrist_hash ^= ZOBRIST_EN_PASSANT[square]


        if piece_type == 3 and not(move.old_has_moved):
            if friendly_castling[0] and start_square % 8 == 0:
                # lost queenside castling #
                zobrist_hash ^= ZOBRIST_CASTLING[(color, 0)]
            elif friendly_castling[1] and start_square % 8 == 7:
                # lost kingside castling #
                zobrist_hash ^= ZOBRIST_CASTLING[(color, 1)]
        if not(move.is_castle) and piece_type == 5 and not(move.old_has_moved):
            # lost both sides castling #
            for side in range(2):
                if friendly_castling[side]:
                    zobrist_hash ^= ZOBRIST_CASTLING[(color, side)]
        if captured_type == 3 and not(move.captured_has_moved):
            opposite_color = BLACK if color == WHITE else WHITE
            if enemy_castling[0] and end_square % 8 == 0:
                # ENEMY lost queenside castling #
                zobrist_hash ^= ZOBRIST_CASTLING[(opposite_color, 0)]
            elif enemy_castling[1] and end_square % 8 == 7:
                # ENEMY lost kingside castling #
                zobrist_hash ^= ZOBRIST_CASTLING[(opposite_color, 1)]

        if move.is_castle: # lost both castling rights
            if friendly_castling[0]:
                zobrist_hash ^= ZOBRIST_CASTLING[(color, 0)]
            if friendly_castling[1]:
                zobrist_hash ^= ZOBRIST_CASTLING[(color, 1)]

            if end_col > start_col: # kingside castle
                zobrist_hash ^= ZOBRIST_PIECES[(3, color, start_row * 8 + 7)]
                zobrist_hash ^= ZOBRIST_PIECES[(3, color, start_row * 8 + 5)]
            else:  # queenside castle
                zobrist_hash ^= ZOBRIST_PIECES[(3, color, start_row * 8 + 0)]
                zobrist_hash ^= ZOBRIST_PIECES[(3, color, start_row * 8 + 3)]

        return zobrist_hash 

    
