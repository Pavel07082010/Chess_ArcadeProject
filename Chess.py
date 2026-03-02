import arcade
import os
import time
from datetime import datetime

white = 'white'
black = 'black'
letters = 'ABCDEFGH'

window_width = arcade.window_commands.get_display_size()[0]
window_height = arcade.window_commands.get_display_size()[1]
board_size = 8
cell_size = int((window_height * 0.9) // board_size)
board_width = cell_size * board_size
board_offset_x = (window_width - board_width) // 2
board_offset_y = (window_height - board_width) // 2

white_color = (210, 210, 210)
black_color = (100, 100, 100)
possible_move_color = (0, 255, 0, 80)
last_move_color = (0, 0, 255, 80)
check_color = (255, 100, 100, 120)
checkmate_color = (255, 50, 50, 180)
castling_color = (255, 255, 0, 80)
en_passant_color = (255, 165, 0, 80)

font_name = "Comic Sans MS"
sprites_path = "sprites"


def opponent(color):
    return black if color == white else white


def int_coords(row):
    return letters.index(row)


def str_coords(row):
    return letters[row]


def correct_coords(row, col):
    return 0 <= row < 8 and 0 <= col < 8


def get_square_color(row, col):
    return white if (row + col) % 2 == 0 else black


def get_piece_sprite_path(piece_type, piece_color, square_color):
    color_prefix = 'w' if piece_color == white else 'b'
    square_suffix = 'white' if square_color == white else 'black'
    sprite_path = os.path.join(sprites_path, f"{color_prefix}{piece_type}_{square_suffix}.png")
    if not os.path.exists(sprite_path):
        sprite_path = os.path.join(sprites_path, f"{color_prefix}{piece_type}.png")
    return sprite_path


class GameResult:
    def __init__(self):
        self.games = []
        self.current_game_start = None
        self.last_result = None
        self.show_result_popup = False
        self.popup_start_time = 0
        self.popup_duration = 5

    def start_game(self):
        self.current_game_start = time.time()
        self.last_result = None
        self.show_result_popup = False

    def end_game(self, winner):
        if self.current_game_start:
            game_time = time.time() - self.current_game_start
            minutes = int(game_time // 60)
            seconds = int(game_time % 60)
            time_str = f"{minutes:02d}:{seconds:02d}"
            winner_name = "Ничья"
            if winner == white:
                winner_name = "Белые"
            elif winner == black:
                winner_name = "Черные"
            result = {
                "date": datetime.now().strftime("%d.%m.%Y %H:%M"),
                "white": "Белые",
                "black": "Черные",
                "winner": winner_name,
                "time": time_str
            }
            self.games.append(result)
            self.last_result = result
            self.show_result_popup = True
            self.popup_start_time = time.time()
            self.current_game_start = None

    def clear_history(self):
        self.games = []

    def update_popup(self):
        if self.show_result_popup:
            if time.time() - self.popup_start_time > self.popup_duration:
                self.show_result_popup = False


class ChessPiece:
    def __init__(self, color):
        self.color = color
        self.has_moved = False
        self.sprite = None
        self.current_square_color = None

    def get_color(self):
        return self.color

    def char(self):
        return self.__class__.__name__[0]

    def set_has_moved(self, moved=True):
        self.has_moved = moved

    def load_sprite(self, square_color):
        piece_type = self.char()
        sprite_path = get_piece_sprite_path(piece_type, self.color, square_color)
        if os.path.exists(sprite_path):
            self.sprite = arcade.Sprite(sprite_path)
            self.sprite.width = cell_size * 0.8
            self.sprite.height = cell_size * 0.8
            self.current_square_color = square_color
            return True
        else:
            default_path = os.path.join(sprites_path, f"{'w' if self.color == white else 'b'}{piece_type}.png")
            if os.path.exists(default_path):
                self.sprite = arcade.Sprite(default_path)
                self.sprite.width = cell_size * 0.8
                self.sprite.height = cell_size * 0.8
                self.current_square_color = square_color
                return True
            else:
                self.sprite = None
                return False

    def update_sprite_for_square(self, square_color):
        if self.current_square_color != square_color:
            self.load_sprite(square_color)


class Rook(ChessPiece):
    def char(self):
        return 'R'

    def can_move(self, board, row, col, row1, col1):
        if row != row1 and col != col1:
            return False
        if row != row1:
            step = 1 if (row1 >= row) else -1
            for r in range(row + step, row1, step):
                if not (board.get_piece(r, col) is None):
                    return False
        else:
            step = 1 if (col1 >= col) else -1
            for c in range(col + step, col1, step):
                if not (board.get_piece(row, c) is None):
                    return False
        return True

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(board, row, col, row1, col1)


class Knight(ChessPiece):
    def char(self):
        return 'N'

    def can_move(self, board, row, col, row1, col1):
        return (abs(row - row1) == 2 and abs(col - col1) == 1) or (abs(row - row1) == 1 and abs(col - col1) == 2)

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(board, row, col, row1, col1)


class Bishop(ChessPiece):
    def char(self):
        return 'B'

    def can_move(self, board, row, col, row1, col1):
        if abs(row - row1) != abs(col - col1):
            return False
        step_row = 1 if (row1 >= row) else -1
        step_col = 1 if (col1 >= col) else -1
        r = row + step_row
        c = col + step_col
        while r != row1 or c != col1:
            if not (board.get_piece(r, c) is None):
                return False
            r += step_row
            c += step_col
        return True

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(board, row, col, row1, col1)


class Queen(ChessPiece):
    def char(self):
        return 'Q'

    def can_move(self, board, row, col, row1, col1):
        if row == row1 or col == col1:
            return Rook.can_move(self, board, row, col, row1, col1)
        elif abs(row - row1) == abs(col - col1):
            return Bishop.can_move(self, board, row, col, row1, col1)
        return False

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(board, row, col, row1, col1)


class King(ChessPiece):
    def char(self):
        return 'K'

    def can_move(self, board, row, col, row1, col1):
        return max(abs(row - row1), abs(col - col1)) == 1

    def can_attack(self, board, row, col, row1, col1):
        return self.can_move(board, row, col, row1, col1)

    def can_castle(self, board, row, col, row1, col1):
        if self.has_moved:
            return False
        if board.is_under_attack(row, col, opponent(self.color)):
            return False
        if col1 > col:
            rook_col = 7
            step = 1
        else:
            rook_col = 0
            step = -1
        rook = board.get_piece(row, rook_col)
        if rook is None or not isinstance(rook, Rook) or rook.has_moved:
            return False
        for c in range(col + step, rook_col, step):
            if board.get_piece(row, c) is not None:
                return False
        for c in range(col, col1 + step, step):
            if c != col and board.is_under_attack(row, c, opponent(self.color)):
                return False
        return True


class Pawn(ChessPiece):
    def __init__(self, color):
        super().__init__(color)
        self.en_passant_target = None

    def char(self):
        return 'P'

    def can_move(self, board, row, col, row1, col1):
        if col != col1:
            return False
        if self.color == white:
            direction = 1
            start_row = 1
        else:
            direction = -1
            start_row = 6
        if row + direction == row1:
            return board.get_piece(row1, col1) is None
        if (row == start_row and row + 2 * direction == row1 and
                board.get_piece(row + direction, col) is None and
                board.get_piece(row1, col1) is None):
            return True
        return False

    def can_attack(self, board, row, col, row1, col1):
        direction = 1 if (self.color == white) else -1
        return (row + direction == row1 and abs(col - col1) == 1)

    def can_en_passant(self, board, row, col, row1, col1):
        direction = 1 if (self.color == white) else -1
        if row + direction != row1 or abs(col - col1) != 1:
            return False
        enemy_pawn = board.get_piece(row, col1)
        if enemy_pawn is None or not isinstance(enemy_pawn, Pawn) or enemy_pawn.get_color() == self.color:
            return False
        if not hasattr(enemy_pawn, 'en_passant_target') or enemy_pawn.en_passant_target is None:
            return False
        if (row1, col1) != enemy_pawn.en_passant_target:
            return False
        return True


class Board:
    def __init__(self):
        self.color = white
        self.field = [[None for _ in range(8)] for _ in range(8)]
        self.last_move = None
        self.move_history = []
        self.check_positions = []
        self.checkmate_positions = []
        self.en_passant_target = None
        self.setup_board()

    def setup_board(self):
        self.field[0] = [Rook(white), Knight(white), Bishop(white), Queen(white),
                         King(white), Bishop(white), Knight(white), Rook(white)]
        self.field[1] = [Pawn(white), Pawn(white), Pawn(white), Pawn(white),
                         Pawn(white), Pawn(white), Pawn(white), Pawn(white)]
        self.field[6] = [Pawn(black), Pawn(black), Pawn(black), Pawn(black),
                         Pawn(black), Pawn(black), Pawn(black), Pawn(black)]
        self.field[7] = [Rook(black), Knight(black), Bishop(black), Queen(black),
                         King(black), Bishop(black), Knight(black), Rook(black)]
        for row in range(8):
            for col in range(8):
                piece = self.field[row][col]
                if piece:
                    square_color = get_square_color(row, col)
                    piece.load_sprite(square_color)
                    if isinstance(piece, Pawn):
                        piece.en_passant_target = None
        self.check_positions = []
        self.checkmate_positions = []
        self.en_passant_target = None

    def current_player_color(self):
        return self.color

    def get_piece(self, row, col):
        if correct_coords(row, col):
            return self.field[row][col]
        return None

    def is_under_attack(self, row, col, color):
        for r in range(8):
            for c in range(8):
                piece = self.field[r][c]
                if piece is not None and piece.get_color() == color:
                    if piece.can_attack(self, r, c, row, col):
                        return True
        return False

    def update_check_status(self):
        self.check_positions = []
        self.checkmate_positions = []
        white_king = self.find_king(white)
        if white_king:
            if self.is_under_attack(white_king[0], white_king[1], black):
                if not self.has_any_moves(white):
                    self.checkmate_positions.append(white_king)
                else:
                    self.check_positions.append(white_king)
        black_king = self.find_king(black)
        if black_king:
            if self.is_under_attack(black_king[0], black_king[1], white):
                if not self.has_any_moves(black):
                    self.checkmate_positions.append(black_king)
                else:
                    self.check_positions.append(black_king)

    def has_any_moves(self, color):
        for row in range(8):
            for col in range(8):
                piece = self.field[row][col]
                if piece and piece.get_color() == color:
                    moves = self.get_possible_moves(row, col)
                    if moves:
                        return True
        return False

    def move_piece(self, row, col, row1, col1):
        if not correct_coords(row, col) or not correct_coords(row1, col1):
            return False
        if row == row1 and col == col1:
            return False
        piece = self.field[row][col]
        if piece is None:
            return False
        if piece.get_color() != self.color:
            return False
        target = self.field[row1][col1]
        is_castling = False
        is_en_passant = False
        captured_pawn = None
        if isinstance(piece, King) and abs(col - col1) == 2:
            if piece.can_castle(self, row, col, row1, col1):
                is_castling = True
            else:
                return False
        if isinstance(piece, Pawn):
            if piece.can_en_passant(self, row, col, row1, col1):
                is_en_passant = True
                captured_pawn = self.field[row][col1]
        if not is_castling and not is_en_passant:
            if target is None:
                if not piece.can_move(self, row, col, row1, col1):
                    return False
            else:
                if target.get_color() == piece.get_color():
                    return False
                if not piece.can_attack(self, row, col, row1, col1):
                    return False
        self.last_move = (row, col, row1, col1, piece, target)
        self.en_passant_target = None
        for r in range(8):
            for c in range(8):
                p = self.field[r][c]
                if isinstance(p, Pawn):
                    p.en_passant_target = None
        self.field[row][col] = None
        if is_castling:
            self.field[row1][col1] = piece
            piece.set_has_moved(True)
            if col1 > col:
                rook = self.field[row][7]
                self.field[row][7] = None
                self.field[row][5] = rook
                rook.set_has_moved(True)
                rook.update_sprite_for_square(get_square_color(row, 5))
            else:
                rook = self.field[row][0]
                self.field[row][0] = None
                self.field[row][3] = rook
                rook.set_has_moved(True)
                rook.update_sprite_for_square(get_square_color(row, 3))
        elif is_en_passant:
            self.field[row1][col1] = piece
            piece.set_has_moved(True)
            self.field[row][col1] = None
        else:
            self.field[row1][col1] = piece
            piece.set_has_moved(True)
            if isinstance(piece, Pawn) and abs(row - row1) == 2:
                direction = 1 if piece.get_color() == white else -1
                target_row = row + direction
                piece.en_passant_target = (target_row, col)
                self.en_passant_target = (target_row, col)
        if not is_castling or (is_castling and piece == self.field[row1][col1]):
            new_square_color = get_square_color(row1, col1)
            piece.update_sprite_for_square(new_square_color)
        if isinstance(piece, Pawn):
            if (piece.get_color() == white and row1 == 7) or (piece.get_color() == black and row1 == 0):
                new_piece = Queen(piece.get_color())
                new_piece.load_sprite(new_square_color)
                new_piece.set_has_moved(True)
                self.field[row1][col1] = new_piece
        king_pos = self.find_king(self.color)
        if king_pos and self.is_under_attack(king_pos[0], king_pos[1], opponent(self.color)):
            self.field[row][col] = piece
            self.field[row1][col1] = target
            if is_castling:
                if col1 > col:
                    rook = self.field[row][5]
                    self.field[row][5] = None
                    self.field[row][7] = rook
                else:
                    rook = self.field[row][3]
                    self.field[row][3] = None
                    self.field[row][0] = rook
                piece.set_has_moved(False)
                rook.set_has_moved(False)
            elif is_en_passant:
                self.field[row][col1] = captured_pawn
                piece.set_has_moved(False)
            else:
                if target:
                    target.set_has_moved(False)
                piece.set_has_moved(False)
            old_square_color = get_square_color(row, col)
            piece.update_sprite_for_square(old_square_color)
            for r in range(8):
                for c in range(8):
                    p = self.field[r][c]
                    if isinstance(p, Pawn) and hasattr(p, 'en_passant_target'):
                        p.en_passant_target = None
            if self.last_move and self.last_move[4] and isinstance(self.last_move[4], Pawn) and abs(self.last_move[2] - self.last_move[0]) == 2:
                last_piece = self.last_move[4]
                last_direction = 1 if last_piece.get_color() == white else -1
                last_target_row = self.last_move[0] + last_direction
                last_piece.en_passant_target = (last_target_row, self.last_move[1])
                self.en_passant_target = (last_target_row, self.last_move[1])
            return False
        self.update_check_status()
        self.color = opponent(self.color)
        return True

    def find_king(self, color):
        for row in range(8):
            for col in range(8):
                piece = self.field[row][col]
                if isinstance(piece, King) and piece.get_color() == color:
                    return (row, col)
        return None

    def get_possible_moves(self, row, col):
        piece = self.field[row][col]
        if piece is None:
            return []
        moves = []
        for row1 in range(8):
            for col1 in range(8):
                if self.is_valid_move(row, col, row1, col1):
                    moves.append((row1, col1))
        if isinstance(piece, King) and not piece.has_moved:
            if piece.can_castle(self, row, col, row, col + 2):
                moves.append((row, col + 2))
            if piece.can_castle(self, row, col, row, col - 2):
                moves.append((row, col - 2))
        if isinstance(piece, Pawn):
            direction = 1 if piece.get_color() == white else -1
            for delta_col in [-1, 1]:
                target_col = col + delta_col
                if 0 <= target_col < 8:
                    target_row = row + direction
                    if piece.can_en_passant(self, row, col, target_row, target_col):
                        moves.append((target_row, target_col))
        return moves

    def is_valid_move(self, row, col, row1, col1):
        piece = self.field[row][col]
        if piece is None:
            return False
        if piece.get_color() != self.color:
            return False
        target = self.field[row1][col1]
        if target is None:
            if not piece.can_move(self, row, col, row1, col1):
                return False
        else:
            if target.get_color() == piece.get_color():
                return False
            if not piece.can_attack(self, row, col, row1, col1):
                return False
        original_piece = self.field[row][col]
        original_target = self.field[row1][col1]
        self.field[row][col] = None
        self.field[row1][col1] = piece
        king_pos = self.find_king(self.color)
        valid = not (king_pos and self.is_under_attack(king_pos[0], king_pos[1], opponent(self.color)))
        self.field[row][col] = original_piece
        self.field[row1][col1] = original_target
        return valid


class ChessGame(arcade.Window):
    def __init__(self):
        super().__init__(window_width, window_height, "Шахматы", fullscreen=True)
        self.board = None
        self.selected_piece = None
        self.selected_row = None
        self.selected_col = None
        self.possible_moves = []
        self.game_over = False
        self.winner = None
        self.piece_sprites = arcade.SpriteList()
        self.game_result = GameResult()
        arcade.set_background_color(arcade.color.DARK_SLATE_GRAY)
        self.setup()

    def setup(self):
        self.board = Board()
        self.selected_piece = None
        self.selected_row = None
        self.selected_col = None
        self.possible_moves = []
        self.game_over = False
        self.winner = None
        self.piece_sprites = arcade.SpriteList()
        for row in range(8):
            for col in range(8):
                piece = self.board.field[row][col]
                if piece and piece.sprite:
                    piece.sprite.center_x = board_offset_x + col * cell_size + cell_size // 2
                    piece.sprite.center_y = board_offset_y + (7 - row) * cell_size + cell_size // 2
                    self.piece_sprites.append(piece.sprite)
        self.game_result.start_game()
        self.board.update_check_status()

    def on_draw(self):
        self.clear()
        self.draw_board()
        self.draw_check_highlight()
        self.piece_sprites.draw()
        self.draw_ui()
        self.draw_result_popup()

    def draw_board(self):
        for row in range(board_size):
            for col in range(board_size):
                color = white_color if (row + col) % 2 == 0 else black_color
                x = board_offset_x + col * cell_size
                y = board_offset_y + (7 - row) * cell_size
                arcade.draw_lrbt_rectangle_filled(x, x + cell_size, y, y + cell_size, color)
                if self.board.last_move:
                    _, _, last_row, last_col, _, _ = self.board.last_move
                    if (row, col) == (last_row, last_col):
                        arcade.draw_lrbt_rectangle_filled(x, x + cell_size, y, y + cell_size, last_move_color)
                if (row, col) in self.possible_moves:
                    is_castling = False
                    is_en_passant = False
                    if self.selected_piece and isinstance(self.selected_piece, King):
                        if abs(self.selected_col - col) == 2:
                            is_castling = True
                    if self.selected_piece and isinstance(self.selected_piece, Pawn):
                        if abs(self.selected_col - col) == 1 and abs(self.selected_row - row) == 1:
                            if self.board.field[row][col] is None:
                                is_en_passant = True
                    if is_castling:
                        arcade.draw_lrbt_rectangle_filled(x, x + cell_size, y, y + cell_size, castling_color)
                    elif is_en_passant:
                        arcade.draw_lrbt_rectangle_filled(x, x + cell_size, y, y + cell_size, en_passant_color)
                    else:
                        arcade.draw_lrbt_rectangle_filled(x, x + cell_size, y, y + cell_size, possible_move_color)
                if self.selected_piece and self.selected_row == row and self.selected_col == col:
                    arcade.draw_lrbt_rectangle_outline(x, x + cell_size, y, y + cell_size, arcade.color.YELLOW, 4)

    def draw_check_highlight(self):
        for pos in self.board.check_positions:
            if pos:
                row, col = pos
                x = board_offset_x + col * cell_size
                y = board_offset_y + (7 - row) * cell_size
                arcade.draw_lrbt_rectangle_filled(x, x + cell_size, y, y + cell_size, check_color)
        for pos in self.board.checkmate_positions:
            if pos:
                row, col = pos
                x = board_offset_x + col * cell_size
                y = board_offset_y + (7 - row) * cell_size
                arcade.draw_lrbt_rectangle_filled(x, x + cell_size, y, y + cell_size, checkmate_color)

    def draw_ui(self):
        current_player = "Белые" if self.board.color == white else "Черные"
        status_text = f"Ход: {current_player}"
        if not self.game_over:
            for pos in self.board.check_positions:
                piece = self.board.get_piece(pos[0], pos[1])
                if piece and piece.get_color() == self.board.color:
                    status_text = f"ШАХ! Ход: {current_player}"
                    break
        if self.game_over:
            if self.winner:
                winner_name = "Белые" if self.winner == white else "Черные"
                status_text = f"МАТ! Победили {winner_name}"
            else:
                status_text = "ПАТ! Ничья"
        arcade.draw_text(status_text, board_offset_x, board_offset_y + board_width + 20,
                         arcade.color.WHITE, 24, font_name=font_name, bold=True)
        if self.game_result.current_game_start:
            game_time = time.time() - self.game_result.current_game_start
            minutes = int(game_time // 60)
            seconds = int(game_time % 60)
            time_text = f"Время: {minutes:02d}:{seconds:02d}"
            arcade.draw_text(time_text, board_offset_x + board_width - 200, board_offset_y + board_width + 20,
                             arcade.color.WHITE, 20, font_name=font_name)
        arcade.draw_text("N - Новая игра  |  ESC - Снять выделение  |  F11 - Полный экран",
                         board_offset_x, board_offset_y - 40, arcade.color.WHITE, 18, font_name=font_name)

    def draw_result_popup(self):
        self.game_result.update_popup()
        if self.game_result.show_result_popup and self.game_result.last_result:
            result = self.game_result.last_result
            popup_width = 500
            popup_height = 300
            popup_x = window_width // 2 - popup_width // 2
            popup_y = window_height // 2 - popup_height // 2
            arcade.draw_lrbt_rectangle_filled(0, window_width, 0, window_height, (0, 0, 0, 150))
            arcade.draw_lrbt_rectangle_filled(popup_x, popup_x + popup_width, popup_y, popup_y + popup_height, (50, 50, 70))
            arcade.draw_lrbt_rectangle_outline(popup_x, popup_x + popup_width, popup_y, popup_y + popup_height, arcade.color.GOLD, 4)
            title = "ПАТ!" if result["winner"] == "Ничья" else "МАТ!"
            title_color = arcade.color.ORANGE if result["winner"] == "Ничья" else arcade.color.GOLD
            arcade.draw_text(title, popup_x + popup_width // 2, popup_y + popup_height - 50,
                             title_color, 48, anchor_x="center", font_name=font_name, bold=True)
            winner_text = f"Победили {result['winner']}!" if result["winner"] != "Ничья" else "Ничья!"
            arcade.draw_text(winner_text, popup_x + popup_width // 2, popup_y + popup_height - 120,
                             arcade.color.WHITE, 32, anchor_x="center", font_name=font_name, bold=True)
            arcade.draw_text(f"Время партии: {result['time']}", popup_x + popup_width // 2, popup_y + popup_height - 180,
                             arcade.color.LIGHT_GRAY, 24, anchor_x="center", font_name=font_name)
            arcade.draw_text(result['date'], popup_x + popup_width // 2, popup_y + popup_height - 220,
                             arcade.color.LIGHT_GRAY, 18, anchor_x="center", font_name=font_name)
            arcade.draw_text("Нажмите любую клавишу или подождите 5 секунд",
                             popup_x + popup_width // 2, popup_y + 30,
                             arcade.color.WHITE, 16, anchor_x="center", font_name=font_name)

    def on_mouse_press(self, x, y, button, modifiers):
        if self.game_result.show_result_popup:
            self.game_result.show_result_popup = False
            return
        if self.game_over:
            return
        if board_offset_x <= x <= board_offset_x + board_width and board_offset_y <= y <= board_offset_y + board_width:
            col = int((x - board_offset_x) // cell_size)
            row = 7 - int((y - board_offset_y) // cell_size)
            if not correct_coords(row, col):
                return
            if self.selected_piece is None:
                piece = self.board.get_piece(row, col)
                if piece and piece.get_color() == self.board.color:
                    self.selected_piece = piece
                    self.selected_row = row
                    self.selected_col = col
                    self.possible_moves = self.board.get_possible_moves(row, col)
            else:
                if (row, col) in self.possible_moves:
                    if self.board.move_piece(self.selected_row, self.selected_col, row, col):
                        self.piece_sprites = arcade.SpriteList()
                        for r in range(8):
                            for c in range(8):
                                piece = self.board.field[r][c]
                                if piece and piece.sprite:
                                    piece.sprite.center_x = board_offset_x + c * cell_size + cell_size // 2
                                    piece.sprite.center_y = board_offset_y + (7 - r) * cell_size + cell_size // 2
                                    self.piece_sprites.append(piece.sprite)
                        self.check_game_over()
                self.selected_piece = None
                self.selected_row = None
                self.selected_col = None
                self.possible_moves = []

    def on_key_press(self, key, modifiers):
        if self.game_result.show_result_popup:
            self.game_result.show_result_popup = False
            return
        if key == arcade.key.N:
            if self.game_result.current_game_start and not self.game_over:
                self.game_result.end_game(None)
            self.setup()
        elif key == arcade.key.ESCAPE:
            self.selected_piece = None
            self.selected_row = None
            self.selected_col = None
            self.possible_moves = []
        elif key == arcade.key.F11:
            self.set_fullscreen(not self.fullscreen)

    def check_game_over(self):
        color = self.board.color
        has_moves = False
        for row in range(8):
            for col in range(8):
                piece = self.board.get_piece(row, col)
                if piece and piece.get_color() == color:
                    moves = self.board.get_possible_moves(row, col)
                    if moves:
                        has_moves = True
                        break
            if has_moves:
                break
        if not has_moves:
            king_pos = self.board.find_king(color)
            if king_pos and self.board.is_under_attack(king_pos[0], king_pos[1], opponent(color)):
                self.game_over = True
                self.winner = opponent(color)
                if king_pos:
                    self.board.field[king_pos[0]][king_pos[1]] = None
                    self.piece_sprites = arcade.SpriteList()
                    for r in range(8):
                        for c in range(8):
                            piece = self.board.field[r][c]
                            if piece and piece.sprite:
                                piece.sprite.center_x = board_offset_x + c * cell_size + cell_size // 2
                                piece.sprite.center_y = board_offset_y + (7 - r) * cell_size + cell_size // 2
                                self.piece_sprites.append(piece.sprite)
                    self.board.update_check_status()
                    if self.game_result.current_game_start:
                        self.game_result.end_game(self.winner)
            else:
                self.game_over = True
                self.winner = None
                if self.game_result.current_game_start:
                    self.game_result.end_game(self.winner)


def main():
    window = ChessGame()
    arcade.run()


if __name__ == "__main__":
    main()