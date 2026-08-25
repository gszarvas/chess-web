import random
from chess_rules import Position

TT_EXACT = 0
TT_LOWERBOUND = 1
TT_UPPERBOUND = 2

DEFENSIVE = 0  # for bot personalities
BALANCED = 1   #
AGGRESSIVE = 2 #

class Opponent:
    def __init__(self, difficulty = None, color = 'black'):
        self.difficulty = difficulty 
        self.color = color 
        self.cutoffs = 0
        self.evaluations = 0
        self.transposition_table = {}
        self.killer_moves = [[None, None] for _ in range(10)]  # choose max_depth + 1
        self.tt_order_hits = 0

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
        point_values = {
            ('pawn', 'black') : -100,
            ('bishop', 'black') : -300,
            ('queen', 'black') : -900,
            ('rook', 'black') : -500,
            ('knight', 'black') : -300,
            ('pawn', 'white') : 100,
            ('bishop', 'white') : 300,
            ('queen', 'white') : 900,
            ('rook', 'white') : 500,
            ('knight', 'white') : 300
        }
        score = 0

        wking = board.board[board.white_king_pos[0]][board.white_king_pos[1]] # safe lookup because king always exists on board
        bking = board.board[board.black_king_pos[0]][board.black_king_pos[1]]
        score += self.eval_king_pos(wking, board.white_king_pos) # add king bonus (positive for white)
        score -= self.eval_king_pos(bking, board.black_king_pos) # subtract king bonus (negative for black)

        for i in range(8):
            for j in range(8):
                piece = board.board[i][j]
                if piece is None or piece.piece_type == 'king':
                    continue 

                if piece.piece_type == 'knight':
                    if piece.color == 'white': 
                        if (i == 0 or i == 7 or j == 0 or j == 7):
                            score -= 30
                        if (2 <= i <= 5) and (2 <= j <= 5):
                            score += 30
                    elif piece.color == 'black':
                        if (i == 0 or i == 7 or j == 0 or j == 7):
                            score += 30
                        if (2 <= i <= 5) and (2 <= j <= 5):
                            score -= 30
                    
                elif piece.piece_type == 'rook':
                    if (2 <= i <= 5) or (2 <= j <= 5):
                        if piece.color == 'white':
                            score += 50
                        else:
                            score -= 50
                elif piece.piece_type == 'queen':
                    if (2 <= i <= 5) or (2 <= j <= 5):
                        if piece.color == 'white':
                            score += 50
                        else:
                            score -= 50
                    else:
                        if piece.color == 'white':
                            score -= 30
                        else:
                            score += 30
                elif piece.piece_type == 'pawn':
                    if piece.color == 'white':
                        score += (40 - i*5)
                    else:
                        score -= (i+1) * 5
                elif piece.piece_type == 'bishop':
                    if (-1 <= i - j <= 1):
                        if piece.color == 'white':
                            score += 10
                            if i == j:
                                score += 10
                        else:
                            score -= 10
                            if i == j:
                                score -= 10
                    if 6 <= i + j <= 8:
                        if piece.color == 'white':
                            score += 10
                            if i + j == 7:
                                score += 10
                        else:
                            score -= 10
                            if i + j == 7:
                                score -= 10
                score += point_values[(piece.piece_type, piece.color)]

        return score 
    
    def minimax(self, board, depth, color, alpha, beta, ply = 0):  # ply useful for killer moves 
        alpha_orig = alpha 
        beta_orig = beta 
        if depth == 0:
            self.evaluations += 1
            return self.evaluate_board(board), None  # return score, move 

        pos = Position(board, color)
        preferred_move = None 
        entry = self.transposition_table.get(pos)
        if entry is not None:
            preferred_move = entry.get('move')
            if entry['depth'] >= depth:
                tt_score = entry['score']
                tt_flag = entry['flag']
                if tt_flag == TT_EXACT:
                    return tt_score, preferred_move
                elif tt_flag == TT_LOWERBOUND:
                    alpha = max(alpha, tt_score)
                elif tt_flag == TT_UPPERBOUND:
                    beta = min(beta, tt_score)
                
                if alpha >= beta:
                    self.tt_order_hits += 1
                    return tt_score, preferred_move
        
        moves = board.get_all_pseudo_moves(color)
        num_white_moves = 0
        num_black_moves = 0
                
        killers = self.killer_moves[ply] if ply < len(self.killer_moves) else [None, None]  ####
        moves.sort(
            key=lambda move: self.move_order_score(move, preferred_move, killers), 
            reverse=True
        )
                
        if color == 'white':
            best_score = -float('inf')
            best_move = None 
            for move in moves:
                board.make_move(move)
                if board.in_check('white'):
                    board.undo_move(move)
                    continue 
                num_white_moves += 1

                position = Position(board, 'black')
                board.pos_history[position] = board.pos_history.get(position, 0) + 1
                if board.pos_history[position] == 3:
                    score = 0
                    # print("Set score to 0 (white)")
                else: 
                    score, _ = self.minimax(board, depth - 1, 'black', alpha, beta, ply + 1)

                board.pos_history[position] -= 1
                if board.pos_history[position] == 0:
                    del board.pos_history[position]

                board.undo_move(move) 

                
                if score > best_score:
                    best_score = score 
                    best_move = move 
                alpha = max(alpha, best_score)
                if alpha >= beta:
                    self.cutoffs += 1
                    if move.captured is None and not move.is_promotion: 
                        self.add_killer_move(ply, move)
                    break 
            if num_white_moves == 0:
                if board.in_check('white'):
                    return -1000000 + ply, None
                else:
                    return 0, None 

        else: # color is black
            best_score = float('inf') 
            best_move = None 
            for move in moves:
                board.make_move(move)
                if board.in_check('black'):
                    board.undo_move(move)
                    continue 
                num_black_moves += 1

                position = Position(board, 'white')
                board.pos_history[position] = board.pos_history.get(position, 0) + 1
                if board.pos_history[position] == 3:
                    score = 0
                    # print("Set score to 0 (black)")
                else:
                    score, _ = self.minimax(board, depth - 1, 'white', alpha, beta, ply + 1)

                board.pos_history[position] -= 1
                if board.pos_history[position] == 0:
                    del board.pos_history[position]

                board.undo_move(move) 

                if score < best_score:
                    best_score = score 
                    best_move = move 
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
                if board.in_check('black'):
                    return 1000000 - ply, None 
                else:
                    return 0, None 


        if color == 'white':
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

        self.transposition_table[pos] = {
            'depth' : depth,
            'score' : best_score,
            'move' : best_move,
            'flag' : flag
        }
        return best_score, best_move

    def move_order_score(self, move, preferred, killers):
        score = move.priority
        if preferred is not None and move.key == preferred.key:
            score += 1000000
        if killers[0] is not None and move.key == killers[0].key:
            score += 9000
        if killers[1] is not None and move.key == killers[1].key:
            score += 8000
        return score 

    def add_killer_move(self, ply, move):
        if ply >= len(self.killer_moves):
            return
        killers = self.killer_moves[ply]

        if move in killers:
            return 
        killers.insert(0, move)
        if len(killers) > 2:
            killers.pop()
        

    
