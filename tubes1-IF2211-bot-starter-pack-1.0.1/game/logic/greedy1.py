import random
from typing import Optional

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction

class Greedy1(BaseLogic):
    def __init__(self):
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.goal_position: Optional[Position] = None
        self.current_direction = 0

    def next_move(self, board_bot: GameObject, board: Board):
        props = board_bot.properties
        # Analyze new state
        if props.diamonds == 5:
            # Move to base
            base = board_bot.properties.base
            self.goal_position = base
            
        current_position = board_bot.position
        if not self.goal_position or current_position == self.goal_position or current_position == board_bot.properties.base:
            diam: GameObject = board.diamonds[0]
            self.goal_position = diam.position
            
        if self.goal_position:
            # We are aiming for a specific position, calculate delta
            delta_x, delta_y = get_direction(
                current_position.x,
                current_position.y,
                self.goal_position.x,
                self.goal_position.y,
            )
            
        return delta_x, delta_y
