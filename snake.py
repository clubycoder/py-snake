import curses
from enum import Enum
from collections import deque
import random
from board import Board
from heart import Heart


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class Snake:
    START_LENGTH = 3
    SPEED = 4.0  # Spots per second
    COLOR_HEAD = 4
    COLOR_TAIL = 5

    def __init__(self, board: Board):
        curses.init_pair(Snake.COLOR_HEAD, curses.COLOR_GREEN, curses.COLOR_BLACK)
        self.style_head = curses.color_pair(Snake.COLOR_HEAD) | curses.A_BOLD
        curses.init_pair(Snake.COLOR_TAIL, curses.COLOR_GREEN, curses.COLOR_YELLOW)
        self.style_tail = curses.color_pair(Snake.COLOR_TAIL) | curses.A_BOLD

        self.board = board
        self.needs_draw = True
        self.pieces = deque()
        self.pieces.appendleft(board.get_start())
        self.old_pieces = []
        self.speed = Snake.SPEED
        self.direction = Direction.DOWN
        self.move_time = 0.0
        self.score = 0
        self.dead = False

        self.board.set_scoreboard("Hearts: %d" % (self.score))

    def input(self, key: int):
        # Handle the moves and make sure you can't move backwards
        # and run in to yourself
        match key:
            case curses.KEY_UP if self.direction != Direction.DOWN:
                self.direction = Direction.UP
            case curses.KEY_DOWN if self.direction != Direction.UP:
                self.direction = Direction.DOWN
            case curses.KEY_LEFT if self.direction != Direction.RIGHT:
                self.direction = Direction.LEFT
            case curses.KEY_RIGHT if self.direction != Direction.LEFT:
                self.direction = Direction.RIGHT

    def update(self, delta: float):
        self.move_time += delta
        mode_time_needed = 1.0 / self.speed
        while self.move_time >= mode_time_needed:
            self.move_time -= mode_time_needed
            (head_x, head_y) = self.pieces[0]
            keep_tail = False
            match self.direction:
                case Direction.UP:
                    head_y -= 1
                case Direction.DOWN:
                    head_y += 1
                case Direction.LEFT:
                    head_x -= 1
                case Direction.RIGHT:
                    head_x += 1
            self.pieces.appendleft((head_x, head_y))
            collided_with = self.board.collision(head_x, head_y)
            if collided_with is not None:
                if isinstance(collided_with, Board):
                    self.dead = True
                    self.board.set_message("You ran in to wall!")
                elif isinstance(collided_with, Snake):
                    self.dead = True
                    if collided_with == self:
                        self.board.set_message("You ran in to yourself!")
                    else:
                        self.board.set_message("You ran in to a snake!")
                elif isinstance(collided_with, Heart):
                    keep_tail = True
                    collided_with.eat()
                    self.score += 1
                    self.board.set_scoreboard("Hearts: %d" % (self.score))
                    self.board.set_message(random.choice(["Nice!", "Good job!", "Woot!", "Nom nom nom!"]))
            if not keep_tail and len(self.pieces) > Snake.START_LENGTH:
                self.old_pieces.append(self.pieces.pop())
            self.needs_draw = True

    def draw(self):
        if self.needs_draw:
            self.needs_draw = False
            if len(self.pieces) > 0:
                # Draw the head
                (head_x, head_y) = self.pieces[0]
                self.board.draw_char(head_x, head_y, "◘", self.style_head)
                if len(self.pieces) > 1:
                    # Draw the neck, but clear the previous head character first
                    (neck_x, neck_y) = self.pieces[1]
                    self.board.draw_char(neck_x, neck_y, None)
                    self.board.draw_char(neck_x, neck_y, "▒", self.style_tail)
            # Clear the old pieces
            if len(self.old_pieces) > 0:
                for (piece_x, piece_y) in self.old_pieces:
                    self.board.draw_char(piece_x, piece_y, None)
                self.old_pieces.clear()

    def collision(self, x, y):
        if len(self.pieces) > 1:
            for piece_num in range(1, len(self.pieces)):
                (piece_x, piece_y) = self.pieces[piece_num]
                if x == piece_x and y == piece_y:
                    return self
        return None
