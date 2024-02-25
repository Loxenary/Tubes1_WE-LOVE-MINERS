import random
from typing import Optional, List

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction

class Greedy2(BaseLogic):
    def __init__(self):
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.goal_position: Optional[Position] = None
        self.returnHome = False
        self.current_direction = 0
        self.diamondDensity = 1
        
    def block_distance(self, a: Position, b: Position):
        return abs(a.x - b.x) + abs(a.y - b.y)
    
    def priorityPoints(self, bot: GameObject, obj: GameObject) -> float: 
        props = bot.properties
        dist = self.block_distance(bot.position, obj.position)
        
        if dist == 0:
            return 0
        else:
            if obj.type == "DiamondGameObject":
                if ((props.diamonds + obj.properties.points) > props.inventory_size):
                    return 0
                elif obj.properties.points == 2:
                    return 1.5 / dist
                else:
                    return 1 / dist
            elif obj.type == "DiamondButtonGameObject":
                return 0.8 / dist
        
    def nextGoal(self, bot: GameObject, board: Board):
        max_points = self.priorityPoints(bot, board.diamonds[0])
        goal_pos = board.diamonds[0].position
        
        for obj in board.game_objects:
            if obj.type == "DiamondGameObject" or obj.type == "DiamondButtonGameObject":
                points = self.priorityPoints(bot, obj)
                if points > max_points:
                    max_points = points
                    goal_pos = obj.position
                                
        # Calculate points for returning to home
        home_dist = self.block_distance(bot.position, bot.properties.base)
        if home_dist > 0 and bot.properties.diamonds > 0:
            home_points = 0.5 / home_dist
            seconds_left = bot.properties.milliseconds_left / 1000
            if home_points > max_points or bot.properties.diamonds == 5 or (home_dist * 1.3 > seconds_left):
                goal_pos = bot.properties.base
        
        return goal_pos
    
    def next_move(self, bot: GameObject, board: Board):
        # Find next goal position
        self.goal_position = self.nextGoal(bot, board)
        # print(self.diamondDensity)
            
        # Set movement
        if self.goal_position:
            # We are aiming for a specific position, calculate delta
            delta_x, delta_y = get_direction(
                bot.position.x,
                bot.position.y,
                self.goal_position.x,
                self.goal_position.y,
            )
            
        return delta_x, delta_y