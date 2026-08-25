import pygame 
import cProfile
import pstats 
import asyncio 

from chess_rules import Pawn 
from chess_rules import Board

from chess_rules import Game
from ai import Opponent
from chess_rules import Position

class ChessGUI:
    def __init__(self):
        pygame.init()
        self.game = Game()
        self.selected = None
        self.running = True
        self.game_message = None 
        self.wait_for_promo = None
        self.highlighted_squares = []
        
        self.WIDTH = 720
        self.HEIGHT = 720
        self.SQUARE = 90 

        self.LIGHT = (238, 221, 190)  # brown/tan theme
        self.DARK  = (145, 108, 77)
        # self.LIGHT = (229, 229, 221)  # blue theme
        # self.DARK  = (108, 122, 137)

        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Chess by gszarvas")
        
        self.images = self.load_images()

        self.circle = pygame.Surface((self.SQUARE, self.SQUARE), pygame.SRCALPHA)

        pygame.draw.circle(
            self.circle,
            (150, 150, 150, 140),   # RGBA
            (self.SQUARE//2, self.SQUARE//2),
            12
        )

        self.capture_ring = pygame.Surface((self.SQUARE, self.SQUARE), pygame.SRCALPHA)

        pygame.draw.circle(
            self.capture_ring,
            (150, 150, 150, 140),  
            (self.SQUARE // 2, self.SQUARE // 2),
            self.SQUARE // 2 - 5,
            4
        )

        self.opponent = Opponent()
        self.black_opponent = None
        self.white_opponent = None

        self.promotion_buttons = {}
        self.font = pygame.font.SysFont("arial", 18, bold=True)

        self.mode = None 

    async def start_menu(self):
        title_font = pygame.font.SysFont("arial", 40, bold=True)
        button_font = pygame.font.SysFont("arial", 28)

        buttons = [
            ("Two Player", pygame.Rect(210, 220, 300, 60), 0),
            ("Single Player", pygame.Rect(210, 320, 300, 60), 1),
            ("Bot vs Bot", pygame.Rect(210, 420, 300, 60), 2),
        ]

        # Colors
        BG = (28, 30, 34)              # dark charcoal
        BUTTON = (120, 24, 40)         # deep crimson
        BUTTON_HOVER = (150, 35, 55)   # hover
        TEXT = (240, 240, 240)
        TITLE = (255, 255, 255)

        while True:
            self.screen.fill(BG)

            title = title_font.render("Chess by gszarvas", True, TITLE)
            self.screen.blit(title, (self.WIDTH // 2 - title.get_width() // 2, 100))

            mouse = pygame.mouse.get_pos()

            for text, rect, value in buttons:
                color = BUTTON_HOVER if rect.collidepoint(mouse) else BUTTON

                pygame.draw.rect(self.screen, color, rect, border_radius=12)

                label = button_font.render(text, True, TEXT)
                self.screen.blit(
                    label,
                    (
                        rect.centerx - label.get_width() // 2,
                        rect.centery - label.get_height() // 2,
                    ),
                )

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

                if event.type == pygame.MOUSEBUTTONDOWN:
                    for text, rect, value in buttons:
                        if rect.collidepoint(event.pos):
                            return value                # returns 0, 1, or 2 referring to number of bots to play
            await asyncio.sleep(1/60)

    async def startup(self):
        self.mode = await self.start_menu() 

        if self.mode == 0:  # 0 bots thus two player mode
            await self.run_two_player()

        elif self.mode == 1: # 1 bot thus single player mode
            opp_color = await self.choose_color_menu()
            self.opponent.set_color(opp_color)

            difficulty = await self.difficulty_menu()
            self.opponent.set_difficulty(difficulty)

            await self.run_single_player()

        elif self.mode == 2: # 2 bots thus bot vs bot
            self.black_opponent = Opponent(color = 'black')
            self.white_opponent = Opponent(color = 'white')

            diff = await self.difficulty_menu()
            self.white_opponent.set_difficulty(diff)
            diff = await self.difficulty_menu() 
            self.black_opponent.set_difficulty(diff)

            await self.run_bot_vs_bot()

    async def choose_color_menu(self): # returns the opposite color chosen by user (so the bot takes that color)
        title_font = pygame.font.SysFont("arial", 40, bold=True)
        button_font = pygame.font.SysFont("arial", 28)

        # Colors
        BG = (28, 30, 34)
        BUTTON = (120, 24, 40)
        BUTTON_HOVER = (150, 35, 55)
        TEXT = (245, 245, 245)
        TITLE = (225, 225, 225)

        buttons = [
            ("White", pygame.Rect(120, 320, 200, 70), "black"),
            ("Black", pygame.Rect(400, 320, 200, 70), "white"),
        ]

        while True:
            self.screen.fill(BG)

            title = title_font.render("Choose Your Color", True, TITLE)
            self.screen.blit(
                title,
                (self.WIDTH // 2 - title.get_width() // 2, 140)
            )

            mouse = pygame.mouse.get_pos()

            for text, rect, return_color in buttons:
                color = BUTTON_HOVER if rect.collidepoint(mouse) else BUTTON

                pygame.draw.rect(self.screen, color, rect, border_radius=12)
                pygame.draw.rect(self.screen, (220, 220, 220), rect, 2, border_radius=12)

                label = button_font.render(text, True, TEXT)
                self.screen.blit(
                    label,
                    (
                        rect.centerx - label.get_width() // 2,
                        rect.centery - label.get_height() // 2,
                    ),
                )

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

                if event.type == pygame.MOUSEBUTTONDOWN:
                    for text, rect, return_color in buttons:
                        if rect.collidepoint(event.pos):
                            return return_color
            await asyncio.sleep(1/60) 

    


    async def difficulty_menu(self): # returns 0, 1, 2, 3, 4, 5, 6 for bot difficulty (depth)
        font = pygame.font.SysFont("arial", 36, bold=True)
        title_font = pygame.font.SysFont("arial", 52, bold=True)

        buttons = []

        labels = [
            ("0 - Random", 0),
            ("1 - Easy", 1),
            ("2 - Beginner", 2),
            ("3 - Intermediate", 3),
            ("4 - Intermediate+", 4),
            ("5 - Advanced", 5),
            ("6 - Advanced+", 6)
        ]

        button_width = 320
        button_height = 60
        spacing = 20

        start_y = 80

        for i, (text, depth) in enumerate(labels):
            rect = pygame.Rect(
                self.WIDTH//2 - button_width//2,
                start_y + i*(button_height + spacing),
                button_width,
                button_height
            )
            buttons.append((rect, text, depth))

        while True:
            self.screen.fill((28, 30, 34))

            if self.mode == 1:
                title = title_font.render("Select Bot Difficulty", True, (255,255,255))
            elif self.mode == 2 and self.white_opponent.difficulty is None:
                title = title_font.render("Select White Bot Difficulty", True, (255,255,255))
            elif self.mode == 2 and self.black_opponent.difficulty is None:
                title = title_font.render("Select Black Bot Difficulty", True, (255,255,255))
            
            self.screen.blit(
                title,
                (self.WIDTH//2 - title.get_width()//2, 20)
            )

            mouse = pygame.mouse.get_pos()

            for rect, text, depth in buttons:
                color = (150, 35, 55) if rect.collidepoint(mouse) else (120, 24, 40) 

                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, (220,220,220), rect, 2)

                label = font.render(text, True, (255,255,255))
                self.screen.blit(
                    label,
                    (rect.centerx - label.get_width()//2,
                    rect.centery - label.get_height()//2)
                )

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

                if event.type == pygame.MOUSEBUTTONDOWN:
                    for rect, text, depth in buttons:
                        if rect.collidepoint(event.pos):
                            return depth
            await asyncio.sleep(1/60) 

    def load_images(self):
        images = {
        ("white", "king") : pygame.image.load("assets/wking.png").convert_alpha(),
        ("white", "queen") : pygame.image.load("assets/wqueen.png").convert_alpha(),
        ("white", "bishop") : pygame.image.load("assets/wbishop.png").convert_alpha(),
        ("white", "rook") : pygame.image.load("assets/wrook.png").convert_alpha(),
        ("white", "knight") : pygame.image.load("assets/wknight.png").convert_alpha(),
        ("white", "pawn") : pygame.image.load("assets/wpawn.png").convert_alpha(),
        ("black", "king") : pygame.image.load("assets/bking.png").convert_alpha(),
        ("black", "queen") : pygame.image.load("assets/bqueen.png").convert_alpha(),
        ("black", "bishop") : pygame.image.load("assets/bbishop.png").convert_alpha(),
        ("black", "rook") : pygame.image.load("assets/brook.png").convert_alpha(),
        ("black", "knight") : pygame.image.load("assets/bknight.png").convert_alpha(),
        ("black", "pawn") : pygame.image.load("assets/bpawn.png").convert_alpha()
    }
        scale = self.SQUARE / 264   # approx. king image height

        for key in images:
            width = images[key].get_width()
            height = images[key].get_height()
            new_width = int(width*scale*1.2)
            new_height = int(height*scale)
            images[key] = pygame.transform.scale(images[key], (new_width, new_height))
        return images 

    def draw_board(self):

        for row in range(8):  # draw squares
            for col in range(8):
                if (row + col) % 2 == 0:
                    color = self.LIGHT
                else:
                    color = self.DARK 
                pygame.draw.rect(self.screen, color, (col*self.SQUARE, row*self.SQUARE, self.SQUARE, self.SQUARE))

        for move in self.highlighted_squares: # draw highlighted squares
            row, col = move.end
            if self.game.game_board.board[row][col] is None:
                self.screen.blit(
                    self.circle,
                    (col * self.SQUARE,
                    row * self.SQUARE)
                )
            else:
                self.screen.blit(
                    self.capture_ring,
                    (col * self.SQUARE, 
                     row * self.SQUARE)
                )
        
        for row in range(8):  # draw pieces
            for col in range(8):
                piece = self.game.game_board.board[row][col]
                if piece is None:
                    continue 
                else:
                    image = self.images[(piece.color, piece.piece_type)]
                    rect = image.get_rect()
                    rect.center = (
                        col * self.SQUARE + self.SQUARE // 2,
                        row * self.SQUARE + self.SQUARE // 2
                    )

                    self.screen.blit(image, rect)

        for col in range(8):  # draw labels
            letter = chr(ord('a') + col)
            # Bottom row is row 7
            color = self.LIGHT if (7 + col) % 2 else self.DARK
            text = self.font.render(letter, True, color)
            self.screen.blit(
                text,
                (
                    col * self.SQUARE + self.SQUARE - 18,
                    8 * self.SQUARE - 20
                )
            )

        for row in range(8):
            number = str(8 - row)
            # Right column is col 7
            color = self.LIGHT if (row + 7) % 2 else self.DARK
            text = self.font.render(number, True, color)
            self.screen.blit(
                text,
                (
                    8 * self.SQUARE - 18,
                    row * self.SQUARE + 4
                )
            )
    
        if self.wait_for_promo is not None:
            overlay = pygame.Surface((self.WIDTH, self.HEIGHT))
            overlay.set_alpha(120)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            menu_width = 400
            menu_height = 120

            menu_x = (self.WIDTH - menu_width) // 2
            menu_y = (self.HEIGHT - menu_height) // 2

            # Background
            pygame.draw.rect(
                self.screen,
                (235, 235, 235),
                (menu_x, menu_y, menu_width, menu_height)
            )

            # Border
            pygame.draw.rect(
                self.screen,
                (0, 0, 0),
                (menu_x, menu_y, menu_width, menu_height),
                3
            )

            pieces = ["queen", "rook", "bishop", "knight"]

            self.promotion_buttons.clear()

            for i, piece in enumerate(pieces):

                image = self.images[(self.game.turn, piece)]

                rect = image.get_rect()

                rect.center = (
                    menu_x + 65 + i * 90,
                    menu_y + menu_height // 2
                )

                self.screen.blit(image, rect)

                self.promotion_buttons[piece] = rect
        
        if self.game.game_over:
            overlay = pygame.Surface((self.WIDTH, self.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 90))
            self.screen.blit(overlay, (0, 0))
    
    def finish_move(self, move):
        if move.captured is None and move.piece.piece_type != 'pawn':
            self.game.fifty_moves += 1
        else:
            self.game.fifty_moves = 0
        if self.game.fifty_moves >= 50:
            self.game_message = "Draw by 50 move rule"
            self.game.game_over = True 
            pygame.display.set_caption("Chess: " + self.game_message)
             
            return 

        self.game.move_history.append(move)
        self.wait_for_promo = None
        self.selected = None
        self.highlighted_squares = []
        self.game.switch_turn()

        position = Position(self.game.game_board, self.game.turn)  # three fold repetition check
        self.game.game_board.pos_history[position] = self.game.game_board.pos_history.get(position, 0) + 1
        if self.game.game_board.pos_history[position] == 3:
            self.game.game_over = True 

            self.game_message = "Draw by threefold repetition"
            pygame.display.set_caption("Chess by gszarvas: " + self.game_message)
            return 

        if self.game.game_board.is_stalemate(self.game.turn):
            self.game_message = "Draw by stalemate"
            self.game.game_over = True 
            pygame.display.set_caption("Chess by gszarvas: " + self.game_message)
            return
        elif self.game.game_board.is_checkmate(self.game.turn):
            winner = 'White' if self.game.turn == 'black' else 'Black'
            self.game_message = f"{winner} wins by checkmate!"
            self.game.game_over = True 
            pygame.display.set_caption("Chess by gszarvas: " + self.game_message)
            return 

    
    def handle_mouse_click(self, pos):
        if self.game.game_over:
            return 
        if self.opponent is None or self.game.turn != self.opponent.color:
            if self.wait_for_promo is not None:
                for piece, rect in self.promotion_buttons.items():
                    if rect.collidepoint(pos):

                        self.wait_for_promo.promotion = piece

                        self.game.game_board.make_move(self.wait_for_promo)
                        self.finish_move(self.wait_for_promo)

                        return

            x, y = pos

            row = y // self.SQUARE
            col = x // self.SQUARE 

            if self.selected is None:
                piece = self.game.game_board.board[row][col]
                if piece is None:
                    self.selected = None 
                elif piece.color != self.game.turn:
                    self.selected = None 
                else: # valid selection
                    self.selected = (row, col)
                    self.highlighted_squares = self.game.game_board.legal_moves(row, col)
                    # highlight legal squares


            else:
                end = (row, col)
                moves = self.game.game_board.legal_moves(self.selected[0], self.selected[1])
                for move in moves:
                    if end[0] == move.end[0] and end[1] == move.end[1]:
                        if move.is_promotion:
                            self.wait_for_promo = move
                            return
                        else:
                            self.game.game_board.make_move(move)
                            self.finish_move(move)
                                
                            break

                    else:
                        continue 

                else:
                    # print("Invalid destination square")
                    self.selected = None
                    self.highlighted_squares = []

    async def run_two_player(self):
        self.opponent = None 
        while self.running:
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False 
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_click(event.pos)
            self.draw_board()
            pygame.display.flip()
            await asyncio.sleep(1/60)

        pygame.quit()
    
    async def run_single_player(self):
        

        while self.running:
            self.draw_board()
            pygame.display.flip() 

            if (not(self.game.game_over) and self.game.turn == self.opponent.color):
                move = self.opponent.choose_move(self.game.game_board)
                # pygame.time.wait(2000)
                if self.opponent.difficulty < 5:
                    pygame.time.wait(500)
                self.game.game_board.make_move(move)
                # print(move.start)
                # print(move.end)
                # print("PASSANT\n") if move.is_passant else print()

                self.finish_move(move)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False 
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_click(event.pos)
            self.draw_board()
            pygame.display.flip()
            await asyncio.sleep(1/60) 

        
        pygame.quit()

    async def run_bot_vs_bot(self):
            
    
            while self.running:
                self.draw_board()
                pygame.display.flip()

                if (not(self.game.game_over) and self.game.turn == self.black_opponent.color): # black's turn
                    move = self.black_opponent.choose_move(self.game.game_board)
                    # pygame.time.wait(2000)
                    if self.black_opponent.difficulty < 5:
                        pygame.time.wait(500)
                    
                    self.game.game_board.make_move(move)
                    # print(move.start)
                    # print(move.end)
                    # print("PASSANT\n") if move.is_passant else print()
    
                    self.finish_move(move)
                    
                elif not(self.game.game_over): # white's turn
                    move = self.white_opponent.choose_move(self.game.game_board)
                    if self.white_opponent.difficulty < 5:
                        pygame.time.wait(500)
                    self.game.game_board.make_move(move)
                    self.finish_move(move)
                    
    
                for event in pygame.event.get(): 
                    if event.type == pygame.QUIT:
                        self.running = False 
                    # if event.type == pygame.MOUSEBUTTONDOWN:
                    #     self.handle_mouse_click(event.pos)
                self.draw_board()
                pygame.display.flip()
                await asyncio.sleep(1/60)
    
            
            pygame.quit()


async def main():
    print("GUI FILE STARTING")
    gui = ChessGUI()
    print("GUI CREATED")
    await gui.startup()

main()

    # gui.opponent.set_difficulty(3)
    # gui.white_opponent.set_difficulty(4)
    # gui.run_single_player()
    # gui.run_bot_vs_bot()


    # print(gui.opponent.cutoffs, gui.opponent.evaluations)

    # board = Board()
    # board.board[1][4] = None 
    # board.board[2][4] = Pawn('white')
    # board.board[2][4].has_moved = True 
    # opp = Opponent()
    # opp.set_difficulty(8)

    # profiler = cProfile.Profile()
    # profiler.enable() 

    # move = opp.choose_move(board)

    # profiler.disable() 

    # stats = pstats.Stats(profiler)
    # stats.sort_stats("cumtime")
    # stats.print_stats(25)      # print the 25 slowest functions

    # print(opp.cutoffs, opp.evaluations, len(opp.transposition_table), opp.tt_order_hits)

