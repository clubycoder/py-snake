import time
import curses
from board import Board
from snake import Snake
from heart import Heart

TARGET_FPS = 60

last_score = 0
best_score = 0


def main(full_screen: curses.window):
    global last_score, best_score

    full_screen.nodelay(True)
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()

    reset = True
    board = None
    snake = None
    heart = None

    paused = False

    done = False
    last_time = time.time_ns()
    num_frames = 0
    seconds = 0.0
    fps = 60
    while not done:
        cur_time = time.time_ns()
        delta = float(cur_time - last_time) / 1000000000.0
        last_time = cur_time

        num_frames += 1
        seconds += delta
        if num_frames % 60 == 0:
            fps = int(num_frames / seconds)
        #    full_screen.addstr(0, 0, "FPS: %-10d" % (fps))
        #if fps > TARGET_FPS:
        #    sleep_time = 1.0 / TARGET_FPS - delta
        #    if sleep_time > 0.0:
        #        time.sleep(sleep_time)

        # Reset game
        if reset:
            reset = False
            board = Board(full_screen)
            snake = Snake(board)
            board.add_child(snake)
            heart = Heart(board)
            board.add_child(heart)

        # Input
        key = full_screen.getch()
        if key == ord('q') or key == curses.KEY_EXIT:
            done = True
        elif key == ord(' '):
            paused = not paused
            board.set_message("Paused..." if paused else "")

        if not done and not paused:
            # Board
            board.input(key)
            board.update(delta)
            board.draw()

            # Snake
            snake.input(key)
            snake.update(delta)
            snake.draw()
            if snake.dead:
                reset = True

            # Heart
            heart.input(key)
            heart.update(delta)
            heart.draw()

        # Refresh
        board.screen_refresh_if_needed()

        last_score = snake.score
        if last_score > best_score:
            best_score = last_score

    full_screen.nodelay(False)


if __name__ == '__main__':
    curses.wrapper(main)
    print("Come back soon!")
    print("Last Score: %d" % (last_score))
    print("Best Score: %d" % (best_score))
