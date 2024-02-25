import random
from typing import Optional, List

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction

class Greedy4(BaseLogic):
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
        dist_to_base = self.block_distance(bot.properties.base, obj.position)
        
        if dist == 0:
            return 0
        else:
            if obj.type == "DiamondGameObject":
                if ((props.diamonds + obj.properties.points) > props.inventory_size):
                    return 0
                elif obj.properties.points == 2:
                    return 1.5 / (dist + (dist_to_base * 0.5))
                else:
                    return 1 / (dist + (dist_to_base * 0.5))
            elif obj.type == "DiamondButtonGameObject":
                points = (1.2 / dist) * self.diamondDensity
                print(f'Button points: {points}')
                return points
        
    def nextGoal(self, bot: GameObject, board: Board):
        max_points = self.priorityPoints(bot, board.diamonds[0])
        goal_pos = board.diamonds[0].position
        self.teleporters = []
        
        diam_dist_total = 0
        diam_dist_max = 0
        diam_count = 0
        
        for obj in board.game_objects:
            if obj.type == "TeleportGameObject":
                self.teleporters.append(obj.position)
            if obj.type == "DiamondGameObject" or obj.type == "DiamondButtonGameObject":
                points = self.priorityPoints(bot, obj)
                if points > max_points:
                    max_points = points
                    goal_pos = obj.position
                
                if obj.type == "DiamondGameObject":
                    diam_count += 1 
                    diam_dist = self.block_distance(bot.properties.base, obj.position)
                    diam_dist_total += diam_dist
                    if diam_dist > diam_dist_max:
                        diam_dist_max = diam_dist
                        
        self.diamondDensity = (diam_dist_total / diam_count) / diam_dist_max
        
        # Calculate points for returning to home
        home_dist = self.block_distance(bot.position, bot.properties.base)
        if home_dist > 0 and bot.properties.diamonds > 0:
            home_points = 0.35 / home_dist
            seconds_left = bot.properties.milliseconds_left / 1000
            if home_points > max_points or bot.properties.diamonds == 5 or (home_dist * 1.7 > seconds_left) or seconds_left < 5:
                goal_pos = bot.properties.base
        
        print(f'Max points: {max_points}')
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