from game import GamePanel, Grid, Game
import random
import time


def default_uniform(grids: list[Grid]):
    valid = []
    currboard = grids[-1].copy()
    explore_up, explore_left, explore_down, explore_right = [currboard.copy() for i in range(4)]
    explore_up.up()
    explore_left.left()
    explore_down.down()
    explore_right.right()
    
    if explore_up != currboard:
        valid.append('w')
    if explore_left != currboard:
        valid.append('a')
    if explore_down != currboard:
        valid.append('s')
    if explore_right != currboard:
        valid.append('d')
    print(valid)
    print(currboard)
    print()
    print(explore_right)
    direction = random.choice(valid)
    print(direction)
    return direction
    
    
if __name__ == '__main__':
    size = 4
    grid = Grid(size)
    panel = GamePanel(grid)
    game2048 = Game(grid, panel, verbose=False)
    final_score = game2048.sim_AI(default_uniform)
    print(f"Final score: {final_score}")
