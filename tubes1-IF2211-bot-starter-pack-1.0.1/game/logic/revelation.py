from abc import ABC
from typing import Tuple
from tkinter import *

from game.logic.base import BaseLogic
from game.models import GameObject, Board, Position
from ..util import get_direction
from math import sqrt, atan
from random import randint

akar2: float = (1/sqrt(2))
def distance(start: Position, end: Position) -> float:
    return sqrt((end.x-start.x)**2+(end.y-start.y)**2)

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
        

def target_check(target: GameObject, board: Board)-> bool:
    if target == None:
        return False
    else:
        for item in board.game_objects:
            if item.position == target.position:
                return True
        return False

def calc_vector(actor: GameObject,target: Position)-> tuple[float,float]:
        pos = actor.position
        print("[VECTOR CALC]",pos,target)
        dist = distance(actor.position,target)
        return (target.x-actor.position.x)/dist,(target.y-actor.position.y)/dist
        #f abs(finish.x - pos.x) >   

def augment_vector(vector: tuple[float,float], mult: float) -> tuple[float,float]:
    return vector[0]*mult,vector[1]*mult

class Revelation(BaseLogic):

    def threat_scan(self,actor: GameObject, board: Board, max_dist: int = 15, normalize: bool = False, invert: bool = False) -> tuple[float,float]:
        threat_x = 0
        threat_y = 0
        hazard_list = board.bots + [object for object in board.game_objects if object.type == "TeleportGameObject"]
        for thing in hazard_list:
            if thing == actor:
                pass
            else:
                delta_x = thing.position.x-actor.position.x
                delta_y = thing.position.y-actor.position.y
                dist = sqrt(delta_x*delta_x+delta_y*delta_y)
                if dist>max_dist:
                    continue
                else:            
                    print(thing.properties.name)
                    direction = round_dir(delta_x,delta_y)
                    if (direction[0] != 0 and direction[1] == 0):
                        threat_x += (max_dist/(delta_x*direction[0]))
                    elif (direction[0] == 0 and direction[1] != 0):
                        threat_y += (max_dist/(delta_y*direction[1]))
                    elif (direction[0] != 0 and direction[1] != 0):
                        threat_x += (max_dist/(delta_x*direction[0]))/2
                        threat_y += (max_dist/(delta_y*direction[1]))/2
        if normalize:
            norm = sqrt(threat_x*threat_x+threat_y*threat_y)
            if norm != 0:
                threat_x = threat_x/norm
                threat_y = threat_y/norm
        if invert:
            threat_x *= -1
            threat_y *= -1
        return threat_x,threat_y
    #1/dist
    
    def __init__(self):
        self.ROOT = Tk()
        self.ROOT.title = "TEST"
        self.boxgrid = [[Label(text="■",fg="gray") for i in range(15)] for j in range(15)]
        for i in range(15):
            for j in range(15):
                self.boxgrid[i][j].grid(row=i,column=j)
        self.has_target = False
        self.target: GameObject
        self.target_location: Position = Position(-1,-1)
        self.prev_pos: Position = [0,0]
        self.going_home: bool = False
    
    
    def set_color(self,row: int, col: int, color: str):
        self.boxgrid[row][col].config(bg= color)

    def refresh_minimap(self, player: GameObject, board: Board):
        for i in range(15):
            for j in range(15):
                self.boxgrid[i][j].config(fg="gray")
                
        for object in board.bots:
            if object == player:
                self.boxgrid[object.position.y][object.position.x].config(fg="yellow")
            else:
                self.boxgrid[object.position.y][object.position.x].config(fg="purple")
        for object in board.diamonds:
            self.boxgrid[object.position.y][object.position.x].config(fg="blue")
        self.ROOT.update() 

    def get_home():
        pass
    
    def ping_targets(self, actor: GameObject, board: Board)-> GameObject: #Algoritma greedy masukin ke sini
        objects = [thing for thing in board.game_objects]
        #diamonds = board.diamonds
        result: GameObject
        best_dist = 99999
        for target in objects:
            if target.type == "DiamondGameObject" or target.type == "DiamondButtonGameObject":
                dist = distance(actor.position,target.position)
                if dist<best_dist:
                    result = target
                    best_dist = dist
        return result
    
    def random_move(self, board_bot: GameObject) -> tuple[int,int]:
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
    
    def next_move(self, board_bot: GameObject, board: Board) -> Tuple[int, int]:
        #self.refresh_minimap(board_bot,board)
        delta_x = 0
        delta_y = 0
        
        if board_bot.properties.diamonds >= 4:
            self.target_location = board_bot.properties.base
            self.has_target = False
            self.going_home = True
        
        elif self.going_home and self.target_location == board_bot.properties.base:
            self.going_home = False
            
        if (not self.going_home): #ping for targets
            if not self.has_target or (self.has_target and board_bot.position == self.target_location):
                self.target = self.ping_targets(board_bot,board)
                self.target_location = self.target.position
                print("TARGET GET",self.target)
                self.has_target = True
        

        if (self.has_target and target_check(self.target,board)) or self.going_home:
            if self.has_target:
                print("SEEKING TARGET")
            elif self.going_home:
                print("GOING HOME")
            else:
                print("INVALID STATE!!!")
            arah = calc_vector(board_bot,self.target_location)
            threat = self.threat_scan(board_bot,board,4,True,True)
            mult = 1.25
            finalle = round_dir(arah[0]*mult+threat[0],arah[1]*mult+threat[1])
            print(arah, threat, finalle)
            if finalle != None:
                delta_x = finalle[0]
                delta_y = finalle[1]
            else:
                x = 0
                y = 0
                if arah[0] == -threat[0]:    
                    while (x == 0):
                        x = self.random_move(board_bot)[0]
                else:
                    while (y == 0):
                        y = self.random_move(board_bot)[0]
                delta_x = x
                delta_y = y 
                        
        else:
            print("INVALID TARGET, ROAMING")
            print("ROAMING")
            print(self.target)
            rand = self.random_move(board_bot)
            delta_x = rand[0]
            delta_y = rand[1]
                
            
        return delta_x, delta_y
        #raise NotImplementedError()
