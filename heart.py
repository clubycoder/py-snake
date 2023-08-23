import curses
from board import Board


class Heart:
    COLOR = 3

    def __init__(self, board: Board):
        curses.init_pair(Heart.COLOR, curses.COLOR_RED, curses.COLOR_BLACK)
        self.style = curses.color_pair(Heart.COLOR) | curses.A_BOLD | curses.A_BLINK

        self.board = board
        self.needs_draw = True
        self.x = 0
        self.y = 0
        self.placed = False

    def input(self, key: int):
        pass

    def update(self, delta: float):
        if not self.placed:
            new_x, new_y = self.board.get_empty_spot()
            if new_x is not None and new_y is not None:
                self.x = new_x
                self.y = new_y
                self.placed = True
                self.needs_draw = True

    def draw(self):
        if self.needs_draw:
            self.needs_draw = False
            if self.placed:
                self.board.draw_char(self.x, self.y, "♥", self.style)
            else:
                self.board.draw_char(self.x, self.y, None)

    def collision(self, x, y):
        if self.placed and x == self.x and y == self.y:
            return self
        return None

    def eat(self):
        self.placed = False
        self.needs_draw = True
