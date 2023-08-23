import random
import curses
from log import log


# A board has a style with a 3x3 shape and a starting point.
# * shape - 3x3 array of booleans for what sections to include.
# * start - (x, y) tuple for which section the player starts in.
#           x is 0 - 2 and y is 0 - 2 matching the above shape.
#           The start is optional and defaults to (1, 1).
class BoardStyle:
    def __init__(self, shape, start=(1, 1)):
        self.shape = shape
        self.start = start


class Board:
    WIDTH = 30
    HEIGHT = int(WIDTH / 2.5)
    COLOR_WALL = 1
    COLOR_FLOOR = 2

    STYLES = [
        BoardStyle(
            [[True, True, True],
             [True, True, True],
             [True, True, True]]
        ),
        BoardStyle(
            [[False, True, True],
             [True, True, True],
             [True, True, False]]
        ),
        BoardStyle(
            [[True, True, False],
             [True, True, True],
             [False, True, True]]
        ),
        BoardStyle(
            [[True, True, True],
             [True, False, True],
             [True, True, True]],
            (0, 0)
        ),
        BoardStyle(
            [[True, True, True],
             [True, False, False],
             [True, True, True]],
            (0, 1)
        ),
        BoardStyle(
            [[True, True, True],
             [False, False, True],
             [True, True, True]],
            (2, 1)
        )
    ]

    def __init__(self, full_screen: curses.window):
        full_screen_height, full_screen_width = full_screen.getmaxyx()
        curses.init_pair(Board.COLOR_WALL, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        self.style_wall = curses.color_pair(Board.COLOR_WALL) | curses.A_BOLD
        curses.init_pair(Board.COLOR_FLOOR, curses.COLOR_WHITE, curses.COLOR_BLACK)
        self.style_floor = curses.color_pair(Board.COLOR_FLOOR)

        self.width = Board.WIDTH
        self.height = Board.HEIGHT
        self.screen_width = self.width + 2
        self.screen_height = self.height + 4
        self.screen_x = int((full_screen_width / 2) - (self.screen_width / 2))
        self.screen_y = int((full_screen_height / 2) - (self.screen_height / 2))
        self.screen = full_screen.subwin(
            self.screen_height,
            self.screen_width,
            self.screen_y,
            self.screen_x
        )
        self.screen_refresh_needed = False

        self.style = random.choice(Board.STYLES)
        self.shape_width = 3
        self.shape_height = 3
        self.shape = self.style.shape
        self.start_x = int((self.width / self.shape_width) / 2) * (self.style.start[0] * 2 + 1)
        self.start_y = int((self.height / self.shape_height) / 2) * (self.style.start[1] * 2 + 1)

        self.screen_background = []
        self.needs_draw = True
        self.usable_spots = []
        for y in range(self.height):
            self.screen_background.append([])
            self.usable_spots.append([])
            for x in range(self.width):
                self.screen_background[y].append(None)
                shape_x = int(x / int(self.width / self.shape_width))
                shape_y = int(y / int(self.height / self.shape_height))
                self.usable_spots[y].append(self.shape[shape_y][shape_x])

        self.children = []

    def input(self, key: int):
        pass

    def update(self, delta: float):
        pass

    def draw(self):
        if self.needs_draw:
            self.needs_draw = False
            self.screen_refresh_needed = True
            for y in range(-1, self.height + 1):
                for x in range(-1, self.width + 1):
                    if self.collision(x, y, True) is not None:
                        # Grab 8 surrounding spots
                        # 0 1 2
                        # 3 x 4
                        # 5 6 7
                        s = [
                            int(self.collision(x - 1, y - 1, True) is not None),
                            int(self.collision(x, y - 1, True) is not None),
                            int(self.collision(x + 1, y - 1, True) is not None),
                            int(self.collision(x - 1, y, True) is not None),
                            int(self.collision(x + 1, y, True) is not None),
                            int(self.collision(x - 1, y + 1, True) is not None),
                            int(self.collision(x, y + 1, True) is not None),
                            int(self.collision(x + 1, y + 1, True) is not None)
                        ]
                        ch = " "
                        # Top or Bottom
                        if s[3] and s[4] and ((not s[6] and (not s[5] or not s[7])) or (not s[1] and (not s[0] or not s[2]))):
                            ch = "═"
                        # Left or Right
                        elif s[1] and s[6] and ((not s[4] and (not s[2] or not s[7])) or (not s[3] and (not s[0] or not s[5]))):
                            ch = "║"
                        # Outside top-left or Inside bottom-right
                        elif s[4] and s[6] and s[1] != s[7]:
                            ch = "╔"
                        # Outside top-right or Inside bottom-left
                        elif s[3] and s[6] and s[1] != s[5]:
                            ch = "╗"
                        # Outside bottom-left or Inside top-right
                        elif s[1] and s[4] and s[6] != s[2]:
                            ch = "╚"
                        # Outside bottom-right or Inside top-left
                        elif s[1] and s[3] and s[6] != s[0]:
                            ch = "╝"
                        self.screen.addch(y + 1, x + 1, ch, self.style_wall)
                    else:
                        ch = "∙"
                        self.screen.addch(y + 1, x + 1, ch, self.style_floor)
                        self.screen_background[y][x] = (ch, self.style_floor)

    def screen_refresh_if_needed(self):
        if self.screen_refresh_needed:
            self.screen_refresh_needed = False
            self.screen.refresh()

    def draw_char(self, x: int, y: int, ch, style=None):
        if x >= 0 and x < self.width and y >= 0 and y < self.height:
            self.screen_refresh_needed = True
            if ch is not None:
                if style is not None:
                    self.screen.addch(y + 1, x + 1, ch, style)
                else:
                    self.screen.addch(y + 1, x + 1, ch)
            else:
                ch = "?"
                attr = self.style_floor
                bg = self.screen_background[y][x]
                if bg is not None:
                    (ch, attr) = bg
                self.screen.addch(y + 1, x + 1, ch, attr)

    def set_scoreboard(self, score: str):
        self.screen_refresh_needed = True
        self.screen.move(self.screen_height - 2, 0)
        self.screen.clrtoeol()
        self.screen.addstr(self.screen_height - 2, 0, score)

    def set_message(self, msg: str):
        self.screen_refresh_needed = True
        self.screen.move(self.screen_height - 1, 0)
        self.screen.clrtoeol()
        self.screen.addstr(self.screen_height - 1, 0, msg)

    def add_child(self, child):
        self.children.append(child)

    def get_start(self):
        return (self.start_x, self.start_y)

    def collision(self, x, y, ignore_children=False):
        # Totally outside of board
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return self
        # Not usable board spot
        if not self.usable_spots[y][x]:
            return self
        if not ignore_children:
            # Spot has a child (snake, heart, etc)
            for child in self.children:
                if child.collision(x, y) is not None:
                    return child
        # No collision
        return None

    def get_empty_spot(self):
        possible_spots = []
        for y in range(self.height):
            for x in range(self.width):
                if not self.collision(x, y):
                    possible_spots.append((x, y))
        if len(possible_spots) > 0:
            random.shuffle(possible_spots)
            return possible_spots[0]
        return None

