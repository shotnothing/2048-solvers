from __future__ import print_function
import tkinter as tk
import tkinter.messagebox as messagebox

import sys
import math
import random


class Grid:
    '''The data structure representation of the 2048 game.
    '''
    def __init__(self, n, cells=None, compressed=False, merged=False, moved=False, current_score=0, is_copy=False):
        self.size = n
        if cells is None:
            self.cells = self.generate_empty_grid()
        else:
            if len(cells) != n or len(cells[0]) != n:
                raise RuntimeError("Grid size mismatch!")
            self.cells = cells
        self.compressed = compressed
        self.merged = merged
        self.moved = moved
        self.current_score = current_score
        self.is_copy = is_copy

    def __str__(self):
        return "\n".join([str(row) for row in self.cells])
    
    def __eq__(self, other):
        check = isinstance(other, Grid)
        if check:
            return self.cells == other.cells
        return check
        
    
    def copy(self):
        return Grid(self.size, cells=[row.copy() for row in self.cells.copy()], compressed=self.compressed, 
                    merged=self.merged, moved=self.moved, current_score=self.current_score, is_copy=True)

    def random_cell(self):
        cell = random.choice(self.retrieve_empty_cells())
        i = cell[0]
        j = cell[1]
        self.cells[i][j] = 2 if random.random() < 0.9 else 4

    def retrieve_empty_cells(self):
        empty_cells = []
        for i in range(self.size):
            for j in range(self.size):
                if self.cells[i][j] == 0:
                    empty_cells.append((i, j))
        return empty_cells

    def generate_empty_grid(self):
        return [[0] * self.size for i in range(self.size)]

    def transpose(self):
        self.cells = [list(t) for t in zip(*self.cells)]

    def reverse(self):
        for i in range(self.size):
            start = 0
            end = self.size - 1
            while start < end:
                self.cells[i][start], self.cells[i][end] = \
                    self.cells[i][end], self.cells[i][start]
                start += 1
                end -= 1

    def clear_flags(self):
        self.compressed = False
        self.merged = False
        self.moved = False

    def left_compress(self):
        self.compressed = False
        new_grid = self.generate_empty_grid()
        for i in range(self.size):
            count = 0
            for j in range(self.size):
                if self.cells[i][j] != 0:
                    new_grid[i][count] = self.cells[i][j]
                    if count != j:
                        self.compressed = True
                    count += 1
        self.cells = new_grid

    def left_merge(self):
        self.merged = False
        for i in range(self.size):
            for j in range(self.size - 1):
                if self.cells[i][j] == self.cells[i][j + 1] and \
                   self.cells[i][j] != 0:
                    self.cells[i][j] <<= 1
                    self.cells[i][j + 1] = 0
                    self.current_score += self.cells[i][j]
                    self.merged = True

    def found_2048(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.cells[i][j] >= 2048:
                    return True
        return False

    def has_empty_cells(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.cells[i][j] == 0:
                    return True
        return False

    def can_merge(self):
        for i in range(self.size):
            for j in range(self.size - 1):
                if self.cells[i][j] == self.cells[i][j + 1]:
                    return True
        for j in range(self.size):
            for i in range(self.size - 1):
                if self.cells[i][j] == self.cells[i + 1][j]:
                    return True
        return False

    def set_cells(self, cells):
        self.cells = cells

    def print_grid(self):
        print('-' * 40)
        for i in range(self.size):
            for j in range(self.size):
                print('%d\t' % self.cells[i][j], end='')
            print()
        print('-' * 40)

    def up(self):
        self.transpose()
        self.left_compress()
        self.left_merge()
        self.moved = self.compressed or self.merged
        self.left_compress()
        self.transpose()

    def left(self):
        self.left_compress()
        self.left_merge()
        self.moved = self.compressed or self.merged
        self.left_compress()

    def down(self):
        self.transpose()
        self.reverse()
        self.left_compress()
        self.left_merge()
        self.moved = self.compressed or self.merged
        self.left_compress()
        self.reverse()
        self.transpose()

    def right(self):
        self.reverse()
        self.left_compress()
        self.left_merge()
        self.moved = self.compressed or self.merged
        self.left_compress()
        self.reverse()


class GamePanel:
    '''The GUI view class of the 2048 game showing via tkinter.'''
    MAX_NUM = 32768
    CELL_PADDING = 10
    BACKGROUND_COLOR = '#92877d'
    EMPTY_CELL_COLOR = '#9e948a'
    SUPERSCRIPT_MAP = {
        "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
        "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"
    }

    CELL_BACKGROUND_COLOR_DICT = {
        '2': '#eee4da',
        '4': '#ede0c8',
        '8': '#f2b179',
        '16': '#f59563',
        '32': '#f67c5f',
        '64': '#f65e3b',
        '128': '#edcf72',
        '256': '#edcc61',
        '512': '#edc850',
        '1024': '#edc53f',
        '2048': '#edc22e',
        '4096': '#eddd2e',
        '8192': '#ed61d2',
        '2¹⁴': '#8c2eed',
        '2¹⁵': '#7646f2',
        'beyond': '#3c3a32'
    }

    CELL_COLOR_DICT = {
        '2': '#776e65',
        '4': '#776e65',
        '8': '#f9f6f2',
        '16': '#f9f6f2',
        '32': '#f9f6f2',
        '64': '#f9f6f2',
        '128': '#f9f6f2',
        '256': '#f9f6f2',
        '512': '#f9f6f2',
        '1024': '#f9f6f2',
        '2048': '#f9f6f2',
        '4096': '#f9f6f2',
        '8192': '#f9f6f2',
        '2¹⁴': '#f9f6f2',
        '2¹⁵': '#f9f6f2',
        'beyond': '#f9f6f2'
    }
    FONT = ('Verdana', 24, 'bold')
    UP_KEYS = ('w', 'W', 'Up')
    LEFT_KEYS = ('a', 'A', 'Left')
    DOWN_KEYS = ('s', 'S', 'Down')
    RIGHT_KEYS = ('d', 'D', 'Right')

    def __init__(self, grid):
        self.grid = grid
        self.root = tk.Tk()
        # if sys.platform == 'win32':
        #    self.root.iconbitmap('2048.ico')
        self.root.title('2048')
        self.root.resizable(False, False)
        self.background = tk.Frame(self.root, bg=GamePanel.BACKGROUND_COLOR)
        self.cell_labels = []
        for i in range(self.grid.size):
            row_labels = []
            for j in range(self.grid.size):
                label = tk.Label(self.background, text='',
                                 bg=GamePanel.EMPTY_CELL_COLOR,
                                 justify=tk.CENTER, font=GamePanel.FONT,
                                 width=4, height=2)
                label.grid(row=i, column=j, padx=10, pady=10)
                row_labels.append(label)
            self.cell_labels.append(row_labels)
        self.background.pack(side=tk.TOP)

    def get_cell_text(self, num):
        string = str(num)
        if len(string) < 5:
            return string
        
        def to_superscript(n):
            return ''.join(GamePanel.SUPERSCRIPT_MAP[d] for d in str(n))

        exponent = int(math.log2(num))
        return "2" + to_superscript(exponent)


    def paint(self):
        for i in range(self.grid.size):
            for j in range(self.grid.size):
                if self.grid.cells[i][j] == 0:
                    self.cell_labels[i][j].configure(
                         text='',
                         bg=GamePanel.EMPTY_CELL_COLOR)
                else:
                    cell_text = self.get_cell_text(self.grid.cells[i][j])
                    if self.grid.cells[i][j] > GamePanel.MAX_NUM:
                        bg_color = GamePanel.CELL_BACKGROUND_COLOR_DICT.get('beyond')
                        fg_color = GamePanel.CELL_COLOR_DICT.get('beyond')
                    else:
                        bg_color = GamePanel.CELL_BACKGROUND_COLOR_DICT.get(cell_text)
                        fg_color = GamePanel.CELL_COLOR_DICT.get(cell_text)
                    self.cell_labels[i][j].configure(
                        text=cell_text,
                        bg=bg_color, fg=fg_color)

class Game:
    '''The main game class which is the controller of the whole game.'''
    AI_DELAY = 1
    def __init__(self, grid, panel, verbose=True):
        self.grid = grid
        self.panel = panel
        self.start_cells_num = 2
        self.over = False
        self.won = False
        self.keep_playing = True
        self.verbose = verbose
        self.history_ai = []

    def is_game_terminated(self):
        return self.over or (self.won and (not self.keep_playing))

    def start(self):
        self.add_start_cells()
        self.panel.paint()
        self.panel.root.bind('<Key>', self.key_handler)
        self.panel.root.mainloop()
        return self.grid.current_score
    
    def sim_AI(self, ai_func):
        self.add_start_cells()
        self.panel.paint()
        
        self.history_ai.append(self.grid.copy())
        self.panel.root.after(Game.AI_DELAY, lambda: self.simulate_step(ai_func))
        self.panel.root.mainloop()
        return self.grid.current_score
    
    def simulate_step(self, ai_func):
            if self.over:
                print('Game over!')
                return self.grid.current_score

            # Strategy here
            direction = ai_func(self.history_ai)
            
            if direction == 'w':
                self.up()
            elif direction == 'd':
                self.right()
            elif direction == 's':
                self.down()
            else:
                self.left()

            #assert ((self.grid.cells == self.history_ai[-1].cells) != self.grid.moved)
            if self.grid.cells != self.history_ai[-1].cells:
                self.history_ai.append(self.grid.copy())
            else:
                self.panel.root.destroy()
                raise RuntimeError("Invalid Move! Move did not change board state")

            self.panel.paint()
            if self.verbose:
                print('Score: {}'.format(self.grid.current_score))

            if self.grid.found_2048():
                self.you_win()
                if not self.keep_playing:
                    print('Game over!')
                    return self.grid.current_score

            if self.grid.moved:
                self.grid.random_cell()

            self.panel.paint()

            if not self.can_move():
                self.over = True
                self.game_over()
                if not self.verbose:
                    self.panel.root.destroy() 
                return self.grid.current_score

            self.panel.root.after(Game.AI_DELAY, lambda: self.simulate_step(ai_func))

    def add_start_cells(self):
        for i in range(self.start_cells_num):
            self.grid.random_cell()

    def can_move(self):
        return self.grid.has_empty_cells() or self.grid.can_merge()

    def key_handler(self, event):
        if self.is_game_terminated():
            if not self.verbose:
                self.panel.root.destroy() 
            return

        self.grid.clear_flags()
        key_value = event.keysym
        if self.verbose:
            print('{} key pressed'.format(key_value))
        if key_value in GamePanel.UP_KEYS:
            self.up()
        elif key_value in GamePanel.LEFT_KEYS:
            self.left()
        elif key_value in GamePanel.DOWN_KEYS:
            self.down()
        elif key_value in GamePanel.RIGHT_KEYS:
            self.right()
        else:
            pass

        self.panel.paint()
        if self.verbose:
            print('Score: {}'.format(self.grid.current_score))

        if self.grid.found_2048():
            self.you_win()
            if not self.keep_playing:
                return

        if self.grid.moved:
            self.grid.random_cell()

        self.panel.paint()
        if not self.can_move():
            self.over = True
            self.game_over()

    def you_win(self):
        if not self.won:
            self.won = True
            if self.verbose:
                print('You Win!')
    

    def game_over(self):
        print('Game over!')
        if self.verbose:
            messagebox.showinfo('2048', 'Oops!\n'
                                    'Game over!')

    def up(self):
        self.grid.up()


    def left(self):
        self.grid.left()
       

    def down(self):
        self.grid.down()
       

    def right(self):
        self.grid.right()
   


if __name__ == '__main__':
    size = 4
    grid = Grid(size)
    panel = GamePanel(grid)
    game2048 = Game(grid, panel, verbose=False)
    final_score = game2048.start()
    print(f"Final score: {final_score}")
