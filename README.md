# chess-python-releases
Public repository for a playable web version of my chess-in-python project

Playable chess game, including checks, checkmate, capturing, castling, en passant. User can choose between two player, one player, or bot vs bot game modes.
In two player, game begins automatically.
In single player, user selects their color and opponent difficulty, and the game begins.
In bot vs bot, user selects white bot difficulty and black bot difficulty, and the game begins. In an active bot vs bot game, no user input is required, only observation.
Click on piece of your color to see its legal moves, and click any highlighted square to move the piece there. 
Click any other square to deselect the chosen piece, and select a piece again. 
Game ends by checkmate, stalemate, draw by threefold repetition or 50 moves.

GitHub Pages Link: https://gszarvas.github.io/chess-web/

Latest updates:
- Significantly reduced search time for the AI opponent
- Optimized in_check, evaluate_board
- Added basic transposition table, iterative deepening, and killer move search for more aggressive pruning and faster search time
- Added playable difficulties (depth) 5 and 6 to the game

Current version: 0.9.4






© 2026 Gergely Szarvas. All rights reserved.
