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
        
        self.buttonPos: Optional[Position] = None
        self.lastUseButton: Optional[int] = None
        
        self.lastGoHome: Optional[int] = None
        
        self.useTel = False
        self.telA: Optional[GameObject] = None
        self.telB: Optional[GameObject] = None
        
    def block_distance(self, a: Position, b: Position):
        return abs(a.x - b.x) + abs(a.y - b.y)
    
    def get_teleporters(self, bot: GameObject, board: Board):
        pos = bot.position
        
        tel: List[GameObject] = []
        for obj in board.game_objects:
            if obj.type == "TeleportGameObject":
                tel.append(obj)
        
        distA = self.block_distance(pos, tel[0].position)
        distB = self.block_distance(pos, tel[1].position)
        
        if distA <= distB:
            return (tel[0], tel[1])
        else:
            return (tel[1], tel[0])
    
    def priorityPoints(self, bot: GameObject, obj: GameObject) -> float: 
        props = bot.properties
        dist = self.block_distance(bot.position, obj.position)
        dist_to_base = self.block_distance(bot.properties.base, obj.position)
        
        dist_with_tel = self.block_distance(bot.position, self.telA.position) + self.block_distance(self.telB.position, obj.position)
        if dist_with_tel < dist and bot.position != self.telA.position:
            self.useTel = True
            dist = dist_with_tel
        else:
            self.useTel = False
        
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
                if self.lastUseButton:
                    return 0
                points = (1.2 / dist) * self.diamondDensity
                # print(f'Button points: {points}')
                if obj.position != self.buttonPos:
                    self.buttonPos = obj.position
                    self.lastUseButton = bot.properties.milliseconds_left
                return points
        
    def nextGoal(self, bot: GameObject, board: Board):
        useTel = False
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
                    goal_pos = self.telA.position if self.useTel else obj.position
                
                if obj.type == "DiamondGameObject":
                    diam_count += 1 
                    diam_dist = self.block_distance(bot.properties.base, obj.position)
                    diam_dist_total += diam_dist
                    if diam_dist > diam_dist_max:
                        diam_dist_max = diam_dist
                        
        self.diamondDensity = (diam_dist_total * 2 / diam_count) / diam_dist_max
        
        # Calculate points for returning to home
        home_dist = self.block_distance(bot.position, bot.properties.base)
        home_dist_tel = self.block_distance(bot.position, self.telA.position) + self.block_distance(self.telB.position, bot.properties.base)
        if home_dist_tel < home_dist and bot.position != self.telA.position:
            home_dist = home_dist_tel
            useTel = True
        else:
            useTel = False
            
        if home_dist > 0 and bot.properties.diamonds > 0:
            home_points = (0.12 * bot.properties.diamonds) / home_dist
            seconds_left = bot.properties.milliseconds_left / 1000
            if (home_points > max_points or bot.properties.diamonds == 5 or seconds_left < 8):
                goal_pos = self.telA.position if useTel else bot.properties.base
        
        print(f'Max points: {max_points}')
        return goal_pos
    
    def next_move(self, bot: GameObject, board: Board):
        # Reset button press
        if self.lastUseButton and (self.lastUseButton - bot.properties.milliseconds_left) > 7000:
            self.lastUseButton = None
        print(self.lastUseButton)
        # Get teleporter position
        tel = self.get_teleporters(bot, board)
        self.telA = tel[0]
        self.telB = tel[1]
        
        # Find next goal position
        self.goal_position = self.nextGoal(bot, board)
        print(self.diamondDensity)
            
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