from game import GamePanel, Grid, Game
import random

def default_uniform(cells: list[list]):
    r = random.random()
    print(cells[-1], end="\n\n")

    if r < 0.25:
        return 'w'
    elif r < 0.5:
        return 'a'
    elif r < 0.75:
        return 's'
    else:
        return 'd'
    
if __name__ == '__main__':
    size = 4
    grid = Grid(size)
    panel = GamePanel(grid)
    game2048 = Game(grid, panel, verbose=False)
    final_score = game2048.sim_AI(default_uniform)
    print(f"Final score: {final_score}")
