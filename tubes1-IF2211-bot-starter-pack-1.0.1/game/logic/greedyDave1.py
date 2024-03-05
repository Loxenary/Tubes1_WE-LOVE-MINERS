from typing import Optional, List

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction

import math

class GreedyDave(BaseLogic):
    def __init__(self):
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.goal_position: Optional[Position] = None
        self.base_distance = 0
        self.current_time = 0
        self.currentId = 0
        self.isDataSaved = False
        # Teleporter which near the user
        self.telA : Optional[GameObject] = None
        # Teleporter which the furthers of the user
        self.telB : Optional[GameObject] = None

        self.redButton : Optional[GameObject] = None

        self.portalErrorHandler : bool = False
    # Calculate Distance between obj2 and obj1
    # returned as float value
    def get_distance(self, obj1 : Position, obj2 : Position):
        return abs(math.sqrt((obj2.x - obj1.x) ** 2 + (obj2.y - obj1.y) ** 2))
    
    def get_obj_by_id(self, obj : List[GameObject], id):
        for ob in obj:
            if(ob.id == id):
                return ob
            
    def get_normalized_distance(self, distance, board : Board):
        max_distance = (board.width **2 + board.height ** 2)**(0.5) 

        return float(distance) / max_distance
            
    def calculateOtherDiamond(self, current_bot: GameObject, board: Board, inventoryWeight, distanceWeight, timeWeight, baseWeight, enemyWeight, isBlueDiamond:  bool):
        
        inventory = current_bot.properties.diamonds
        time_Stamp = current_bot.properties.milliseconds_left / 1000
        
        # The lower the inventory, it is desirable to get the red diamond
        inventory_score = inventory / current_bot.properties.inventory_size
        inventory_score =  1 - inventory_score
        
        diamond_obj = self.getNearestDiamondByOption(current_bot, board, isBlueDiamond=isBlueDiamond)

        if(diamond_obj):
            # The shorter the distance to red diamond, it is better to get the red diamond
            distance = self.get_distance(current_bot.position, diamond_obj.position)

            distance = self.get_normalized_distance(distance, board)
            distance = max(0, 1 - distance)
            if(inventory > diamond_obj.properties.points):
                return 0, diamond_obj.properties.points
        else:
            return 0, current_bot.position 

        # The shorter the time, is it better not to get the red diamond
        time_score = time_Stamp / self.current_time

        if(self.get_amount_of_bots(board) == 1):
            Enemy_Score = 0
        else:
            # The shorter the enemy to Red Diamond, is is better not to get the red diamond
            Enemy_Obj = self.getNearestEnemyFromObj(diamond_obj, board)
            Enemy_Dist = self.get_distance(Enemy_Obj.position, diamond_obj.position)
            Enemy_Dist = self.get_normalized_distance(Enemy_Dist, board)
            Enemy_Score = 1 - Enemy_Dist
        
        c = inventory_score * inventoryWeight
        d = distance * distanceWeight
        t = time_score * timeWeight
        b = self.base_distance * baseWeight
        e = Enemy_Score * enemyWeight

        total_score= inventoryWeight + distanceWeight + timeWeight + baseWeight

        result = (c + d + t + b - e) / total_score

        return result, diamond_obj.position
 
    def getNearestDiamondByOption(self, bot: GameObject, board: Board, isBlueDiamond : bool):
        min_distance = float("inf")
        diamond = None
        for obj in board.diamonds:
            distance_to_Diam = self.get_distance(bot.position, obj.position)

            # Get Nearest Blue Diamond
            if(obj.properties.points == 1 and isBlueDiamond and min_distance > distance_to_Diam):
                min_distance = distance_to_Diam
                diamond = obj

            # Get Nearest Red Diamond
            if(obj.properties.points == 2 and (not isBlueDiamond) and min_distance > distance_to_Diam):
                min_distance = distance_to_Diam
                diamond = obj
        return diamond

    def get_amount_of_bots(self, board: Board):
        return len(board.bots)

    def getNearestEnemyFromObj(self, Obj : GameObject, board: Board):
        min_distance = float("inf")
        enemy_obj = None
        for bot in board.bots:
            distance = self.get_distance(Obj.position, bot.position)
            if(distance < min_distance and (self.currentId != bot.id)):
                enemy_obj = bot
                min_distance = distance

        return enemy_obj

    def calculateGoesToBase(self, current_bot: GameObject, board : Board, inventoryWeight, timeWeight, baseWeight, enemyWeight, nearestDiamWeight):
        
        def getNearestDiamondFromBase(board: Board):
            min_distance = float('inf')
            nearest_diamond = None
            for diamond in board.diamonds:
                distance = self.get_distance(current_bot.properties.base, diamond.position)

                if(min_distance > distance):
                    min_distance = distance
                    nearest_diamond = diamond
            return nearest_diamond

        inventory = current_bot.properties.diamonds
        times = current_bot.properties.milliseconds_left / 1000
        nearest_enemy = None
        nearest_diamond = None

        if(self.base_distance < 0.1):
            return 0, current_bot.properties.base
        if(inventory == 5):
            return 1, current_bot.properties.base

        # The higher the inventory, it is better to go back to base
        inventory_score = inventory / current_bot.properties.inventory_size

        # The shorter the time left, it is better to go back to base
        times_score = (1 - (times / self.current_time))
        

        if(self.get_amount_of_bots(board) == 1):
            # No Enemy
            nearest_enemy_score = 0
        else:
            # The nearer the enemy to base, it is better not to go to base
            nearest_enemy=  self.getNearestEnemyFromObj(current_bot, board)
            enemy_distance = self.get_distance(current_bot.properties.base, nearest_enemy.position) 
            enemy_distance = self.get_normalized_distance(enemy_distance, board)
            nearest_enemy_score = 1 - enemy_distance

        nearest_diamond = getNearestDiamondFromBase(board)

        if(nearest_diamond):
            # The nearer the diamond to base, it is recommended to go back to base
            nearest_diamond_score = self.get_distance(current_bot.properties.base, nearest_diamond.position)
            nearest_diamond_score = self.get_normalized_distance(nearest_diamond_score, board)
            nearest_diamond_score = max(0, 1 - nearest_diamond_score)
        else:
            nearest_diamond_score = 0

        # If the times reach 5 - 10 get the nearest diamond from base
        if(times > 5 and times < 10 and (current_bot.properties.inventory_size - inventory) >= nearest_diamond.properties.points):
            return 1, nearest_diamond.position
        # If the times reach under 5 and there exist a diamond in inventory then just go back to base
        elif(times <= 5 and inventory >= 1):
            return 1, current_bot.properties.base
        

        if(current_bot.properties.diamonds == 0):
            return 0, current_bot.properties.base
        
        c = inventory_score * inventoryWeight
        b = self.base_distance * baseWeight
        t = times_score * timeWeight
        e = nearest_enemy_score * enemyWeight
        nd = nearest_diamond_score * nearestDiamWeight
        total_score = inventoryWeight + baseWeight + timeWeight + enemyWeight + nearest_diamond_score

        result = (c + b + t + nd - e) / total_score

        return result, current_bot.properties.base
        

    def getNearestDiamond(self, current_bot : GameObject, board: Board):
        min = float("inf")
        diam_obj = None
        for diamond in board.diamonds:
            distance = self.get_distance(current_bot.position, diamond.position)
            if(distance <= min):
                diam_obj = diamond        
                min = distance
        
        return diam_obj
            
    def get_redButton(self, board: Board):
        for obj in board.game_objects:
            if(obj.type == "DiamondButtonGameObject"):
                return obj

    def calculateNearestDiamond(self, current_bot : GameObject, board: Board, inventoryWeight, timeWeight, baseWeight, distanceWeight, pointWeight):
        
        # Consideration
        inventory = current_bot.properties.inventory_size
        time = current_bot.properties.milliseconds_left / 1000
        
        # The lesser the inventory left, is is better to just get the nearest diamond
        inventory_score = inventory / current_bot.properties.inventory_size

        diam_obj = self.getNearestDiamond(current_bot, board)

        if(diam_obj):
            # The shorter the distance of diamond to player, it is more desirable
            distance= self.get_distance(diam_obj.position, current_bot.position)
            distance = self.get_normalized_distance(distance, board)
            distance = max(0, 1 - distance)
            point = diam_obj.properties.points
            point_score = point / 2
        else:
            return 0, current_bot.position
        
        # The shorter the time left, it is better to get the nearest diamond
        time_score = time/ self.current_time
        time_score = 1 - time
        
        if((current_bot.properties.inventory_size - inventory) < point):
            return 0, diam_obj.position

        c = inventory_score * inventoryWeight
        t = time_score * timeWeight
        b = self.base_distance * baseWeight
        d = distance * distanceWeight
        p = point_score * pointWeight
        total_Score =inventoryWeight + timeWeight + baseWeight + distanceWeight + pointWeight

        result = (c + t + b + d + p) / total_Score
        return result, diam_obj.position
        
    def calculateTakePortal(self, bot: GameObject, board: Board, distanceWeight, pointWeight, baseWeight, enemyWeight):
        
        # Reset Portal Error Hanlder
        if(self.portalErrorHandler):
            self.portalErrorHandler = False
            return 0, bot.position

        # Consideration
        Inventory = bot.properties.diamonds
        distance_to_portal = self.get_distance(bot.position,self.telA.position)
    
        # The nearer the diamond to teleporter and the distance from the player, it is desirable to get the diamond
        nearest_diamonds = self.getNearestDiamond(self.telB,board)
        distance_to_diamond = self.get_distance(self.telB.position, nearest_diamonds.position)
        total_Distance_to_diamond = distance_to_portal + distance_to_diamond
        distance_score = self.get_normalized_distance(total_Distance_to_diamond, board)
        distance_score = max(0, 1- distance_score)

        # Diamond Points
        point_score = nearest_diamonds.properties.points / 2

        # The nearer the other portal to base and the higher the inventory size it is more preferable
        inventory_Score = Inventory / bot.properties.inventory_size
        inventory_Score = max(0, 1-inventory_Score)

        distance_to_base = self.get_distance(self.telB.position, bot.properties.base)
        total_base_Distance = self.get_normalized_distance((distance_to_base + distance_to_portal), board)

        base_score = ((inventory_Score) + (total_base_Distance * 2)) / 3

        # The nearer the enemy to portal, it is not desirable to take the portal

        nearest_enemy = self.getNearestEnemyFromObj(self.telB, board)
        if(nearest_enemy):
            distance_enemy = self.get_distance(nearest_enemy.position, self.telB.position)
            enemy_score= max(0, 1-self.get_normalized_distance(distance_enemy,board))
        else:
            enemy_score = 0

        d = distance_score * distanceWeight
        p = point_score * pointWeight
        b = base_score * baseWeight
        e = enemy_score * enemyWeight
        total_score = distanceWeight + pointWeight + baseWeight + enemyWeight

        result = (d + p + b - e) / total_score
        return result, self.telA.position
        

    def calculateTakeRedButton(self, bot : GameObject, board: Board, inventoryWeight, amountWeight, scoreWeight, distanceWeight, enemyWeight):
        # Consideration
        user_inventory = bot.properties.diamonds
        
        # the more the inventory left, it is better to take the red if it is near
        inventory_score= (1 - user_inventory/ bot.properties.inventory_size)
        
        amount_of_diamond = len(board.diamonds)

        # The lesser the diamond on scene, it is more desirable to take the red button
        amount_score = max(0, 1 - amount_of_diamond / 20) # Assumption: max diamond is 20

        # The higher the ratio of current player with other bots, it is less desirable to take the red button
        highest_player_score = max(board.bots, key=lambda x: x.properties.score)
        current_player_score = bot.properties.score

        if(highest_player_score.properties.score != 0):
            scores_ratio = current_player_score / highest_player_score.properties.score
        else:
            print(highest_player_score)
            scores_ratio = 0

        # The shorter the distance, it is also preferable to take the red button
        player_distance= self.get_distance(bot.position, self.redButton.position)
        distance_score = self.get_normalized_distance(player_distance, board)
        distance_score = max(0, 1 - distance_score)

        # The shorter enemy distance to red button, is is not preferable
        nearest_enemy = self.getNearestEnemyFromObj(self.redButton, board)
        if(nearest_enemy):
            enemy_score = self.get_distance(nearest_enemy.position, self.redButton.position)
            enemy_score = self.get_normalized_distance(enemy_score, board)
            enemy_score = max(0, 1- enemy_score)
        else:
            enemy_score = 0

        c = inventory_score * inventoryWeight
        a = amount_score * amountWeight
        s = scores_ratio * scoreWeight
        d = distance_score * distanceWeight
        e = enemy_score * enemyWeight
        total_Score = inventoryWeight + amountWeight + scoreWeight + distanceWeight + enemyWeight

        result = (c + a + s + d - e) / total_Score
        return result, self.redButton.position
    
    # Niru kode qaiz mager buatnya
    def get_teleports(self, bot: GameObject, board: Board):
        pos = bot.position
        
        tel: List[GameObject] = []
        for obj in board.game_objects:
            if obj.type == "TeleportGameObject":
                tel.append(obj)
        
        distA = self.get_distance(pos, tel[0].position)
        distB = self.get_distance(pos, tel[1].position)
        
        if distA <= distB:
            return (tel[0], tel[1])
        else:
            return (tel[1], tel[0])
    
    def nextGoal(self, bot: GameObject, board: Board):
        
        tel = self.get_teleports(bot, board)
        self.telA = tel[0]
        self.telB = tel[1]

        self.redButton = self.get_redButton(board)

        bd = self.get_distance(bot.position, bot.properties.base)
        bd = self.get_normalized_distance(bd,board)
        self.base_distance = max(0, 1-bd)

        target_names = ["Nearest Diamond", "Blue Diamond","Red Diamond","Base","Portals","Red Button"]
        points = []
        positions = []

        # Nearest Diamond
        point, pos = self.calculateNearestDiamond(bot,board,inventoryWeight=3,timeWeight=2,baseWeight=1,distanceWeight=3,pointWeight=1)
        
        points.append(point); positions.append(pos)

        # Blue Diamond
        point, pos = self.calculateOtherDiamond(bot, board, inventoryWeight=3,distanceWeight=3,timeWeight=2,baseWeight=3,enemyWeight=2,isBlueDiamond=True)

        points.append(point); positions.append(pos)

        # Red Diamond
        point, pos = self.calculateOtherDiamond(bot,board,inventoryWeight=3,distanceWeight=4,timeWeight=2, baseWeight=2,enemyWeight=2, isBlueDiamond=False)
        
        points.append(point); positions.append(pos)

        # Base
        point, pos = self.calculateGoesToBase(bot,board, inventoryWeight=3,timeWeight=1,baseWeight=2,enemyWeight=2,nearestDiamWeight=2)
        
        points.append(point); positions.append(pos)
        
        # Portal
        point, pos = self.calculateTakePortal(bot,board,distanceWeight=4,pointWeight=2,baseWeight=4,enemyWeight=2)

        points.append(point); positions.append(pos)
        
        # Red Button
        point,pos = self.calculateTakeRedButton(bot, board, inventoryWeight=2,amountWeight=4,scoreWeight=2,distanceWeight=2,enemyWeight=2)

        points.append(point); positions.append(pos)

        highest_point = max(points)
        idx = points.index(highest_point)
        highest_pos = positions[idx]

        # Hanlde Portal Error
        if(target_names[idx] == "Portals"):
            self.portalErrorHandler = True

        print("Targets: ", target_names[idx])
        return highest_pos


    def next_move(self, bot: GameObject, board: Board):
        # Find next goal position

        # Save Time
        if(not self.isDataSaved):
            self.current_time = int(round(bot.properties.milliseconds_left / 1000))
            self.currentId = bot.id
            self.isDataSaved = True
            print("Time: ", self.current_time)

        self.goal_position = self.nextGoal(bot,board)

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
        

        
    # def weightMatrix(self, board: Board):


    # def next_move(self, board_bot: GameObject, board: Board):
    #     priority_obj = self.