from abc import ABC
from typing import Tuple


from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from math import sqrt,exp
from random import randint

akar2: float = (1/sqrt(2))

#distance
def dist(start: Position, end: Position) -> float:
    return sqrt((end.x-start.x)**2+(end.y-start.y)**2)

def length(x: float, y: float) -> float:
    return sqrt(x**2 + y**2)

def normalize(x: float, y: float) -> Tuple[float,float]:
    leng = length(x,y)
    if leng == 0:
        return 0,0
    else:
        return x/leng,y/leng

def vector_AB(A: Position, B: Position) -> Tuple[float,float]:
    x = B.x - A.x
    y = B.y - A.y
    return normalize(x,y)

def random_move(board_bot: GameObject) -> tuple[int,int]:
        delta_x = randint(-1,1)
        delta_y = 0
        while(delta_x + board_bot.position.x > 15 or delta_x + board_bot.position.x < 0):
            delta_x = randint(-1,1)
        if delta_x == 0:
            while (delta_y == 0):
                delta_y = randint(-1,1)
                while(delta_x + board_bot.position.x > 15 or delta_x + board_bot.position.x < 0):
                    delta_y = randint(-1,1)
        else:
            delta_y = 0
        return delta_x,delta_y

def taxicab_dist(start: Position, end: Position) -> int:
    return abs(end.x-start.x)+abs(end.y-start.y)

def round_away(angka: float):
    if angka >= 0.5:
        return 1
    elif angka <= 0.5:
        return -1

def round_dir(x: float, y: float, allow_corner = False) -> tuple[float,float]:        
    if allow_corner:
        x = round_dir(x,0)/2
        y = round_dir(0,y)/2
        return x,y
    elif abs(x) > abs(y):
        if x > 0: return 1,0
        else: return -1,0
    elif abs(x) < abs(y):
        if y > 0: return 0,1
        else: return 0,-1
    elif (x != 0 and y != 0):
        result = [round_away(x),round_away(y)]
        verdict = randint(0,1)
        return (result[0]*verdict),(result[1]*(1-verdict))
    else:
        return 0,0

def get_portal(board: Board) -> list[GameObject]:
    return [thing for thing in board.game_objects if thing.type == "TeleportGameObject"]

def sort_portal(actor: GameObject, portals: list[GameObject]) -> list[GameObject]:
    result = [portals[0]]
    if dist(actor.position,portals[1].position) < dist(actor.position,portals[0].position):
        result.insert(0,portals[1])
    else:
        result.insert(1,portals[1])
    return result

def t_func(dist: int, max: int) -> float:
    return ((dist-max)**2)/(max**2)

def p_func(dist: int, max: int) -> float:
    return(exp(-(4*dist)/max))


def valid_move(actor: GameObject, x: int, y: int):
    if x == 0 and y == 0:
        return False
    board_size = 15
    pos = actor.position
    if pos.x == 0 and x < 0:    
        return False
    if pos.x == board_size-1 and x > 0:
        return False
    if pos.y == 0 and y < 0:    
        return False
    if pos.y == board_size-1 and y > 0:
        return False
    return True
    
class Revelation(BaseLogic):

    def __init__(self):
        self.target_type: str = None
        self.portal_cooldown: int = 0
        pass
    
    def calc_pp(self,actor: GameObject,object: GameObject):
        weights = {
            "DiamondGameObject" : 5,
            "DiamondButtonGameObject" : 12,
            "Base" : 2,
            "BotGameObject" : 1,
            "BaseGameObject" : 0
        }
        
        diamonds = actor.properties.diamonds
        inv_size = actor.properties.inventory_size
        
        tipe = object.type
        if tipe == "DiamondGameObject":
            if (diamonds + object.properties.points > inv_size):
                return 0
            else:
                return weights[tipe] * (object.properties.points + 1)
        elif tipe == "Base":
            #print("INV",diamonds,inv_size)
            return weights[tipe] * (actor.properties.diamonds / actor.properties.inventory_size) * 15
        else:
            return weights[tipe]
    
    def ping_target(self,board_bot: GameObject, board: Board) -> Position:
        max_range = 30
        
        base = GameObject(69, board_bot.properties.base, "Base")
        target_list = [object for object in board.game_objects if object != board_bot and object.type in ["DiamondGameObject","DiamondButtonGameObject","BotGameObject"]] + [base]
        best_point : float = 0
        final_target: GameObject
        final_type: str
        portals = sort_portal(board_bot,get_portal(board))
        
        for target in target_list:
            #direct
            try:
                #V2    
                #points = (1-taxicab_dist(board_bot.position,target.position)/max_range) * self.calc_pp(board_bot,target)
                #V3
                points = t_func(taxicab_dist(board_bot.position,target.position),max_range) * self.calc_pp(board_bot,target)
                #print("NORMAL",target.type,points, end = " | ")
                if points > best_point:
                    final_target = target
                    final_type = target.type
                    best_point = points
                
                #portal
                if self.portal_cooldown == 0:
                    #V2
                    #points = (1-(taxicab_dist(board_bot.position,portals[0].position) + taxicab_dist(portals[1].position,target.position))/max_range) * self.calc_pp(board_bot,target)
                    #V3
                    points = t_func(taxicab_dist(board_bot.position,portals[0].position) + 1 + taxicab_dist(portals[1].position,target.position),max_range) * self.calc_pp(board_bot,target)
                    #print("PORTAL",target.type,points)
                    if points > best_point:
                        final_target = portals[0]
                        final_type = target.type
                        best_point = points
                        
            except ZeroDivisionError:
                pass
            self.target_type = final_target.type
        return final_target.position
    
    def threat_scan(self,board_bot: GameObject, fear_dist: int, board: Board) -> Tuple[float,float]:
        threat_list: list[GameObject] = []
        if self.target_type != "BotGameObject" :
            threat_list += [bot for bot in board.bots if bot != board_bot]
        if self.target_type != "TeleportGameObject" :
            threat_list += get_portal(board)
        
        arena_size = 15
        max_dist = arena_size * 2 #taxicab dist
        
        threat_x = 0
        threat_y = 0
        for threat in threat_list:
            distance = taxicab_dist(board_bot.position,threat.position)
            if (distance > fear_dist or distance == 0):
                continue
            else:
                print(threat.type,threat.properties.name)
                direction = round_dir(threat.position.x - board_bot.position.x,threat.position.y - board_bot.position.y)
                print("FEAR",t_func(distance,fear_dist))
                threat_x -= direction[0] * t_func(distance,fear_dist)
                threat_y -= direction[1] * t_func(distance,fear_dist)
        
        if length(threat_x,threat_y) > 1:
            norm_threat = normalize(threat_x,threat_y)
            fix = [norm_threat[0],norm_threat[1]]
        else:
            fix = [threat_x,threat_y]
        
        return fix[0],fix[1]
        
    
    def next_move(self, board_bot: GameObject, board: Board) -> Tuple[int, int]:
        #self.refresh_minimap(board_bot,board)
        if self.portal_cooldown > 0:
            self.portal_cooldown -= 1
        
        if (board_bot.position == sort_portal(board_bot,get_portal(board))[0].position):
            self.portal_cooldown += 3
        priority = self.ping_target(board_bot,board)
        prio_dir = vector_AB(board_bot.position,priority)
        threat_dir = self.threat_scan(board_bot,5,board) #THREAT
        
        delta_x = 0
        delta_y = 0
        
        movdir = round_dir(prio_dir[0] + threat_dir[0], prio_dir[1] + threat_dir[1],False)
        #print("POS",board_bot.position)
        #print(priority,prio_dir,threat_dir,movdir)

        if(not valid_move(board_bot,movdir[0],movdir[1])):
            x = delta_x
            y = delta_y
            print("INVALID MOVE ! | ",end="")
            print(priority,prio_dir,threat_dir,movdir)
            if int(prio_dir[0]) == -int(threat_dir[0]) and prio_dir[0] != 0:
                print("RANDOM Y")
                while(not valid_move(x,y)):
                    y = randint(-1,1)
            elif int(prio_dir[1]) == -int(threat_dir[1]) and prio_dir[1] != 0:
                print("RANDOM X")
                while(not valid_move(x,y)):
                    x = randint(-1,1)
            else:
                print(int(prio_dir[0]) == -int(threat_dir[0]),int(prio_dir[1]) == -int(threat_dir[1]))
                rand = random_move(board_bot)
                x = rand[0]
                y = rand[1]
                
            if (not valid_move(board_bot,x,y)):
                while (not valid_move(board_bot,x,y)):
                    rand = random_move(board_bot)
                    x = rand[0]
                    y = rand[1]
                
            delta_x = x
            delta_y = y
                

            
        delta_x = movdir[0]
        delta_y = movdir[1]
        
        return delta_x, delta_y
        #raise NotImplementedError()
