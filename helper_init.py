import pygame
from helper import *
import os
import sys,csv
from  Object import *
from Slidable import *
from Pushable import *
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
tiles_dimension=(45,45)
enemy_size=(60,90)
CheckP=[]
img_arr=[]
tiles=[]
Slidables=[]
Ladder=[]
Food=[]
Door=[]
Lift=[]
Boxes=[]
Inventory=[]
Damage=[]
Pushables=[]
Danger=[]
Rest=[]
Floor=[]
Enemy=[]
death_screen=loadimages("Assets/Death_screen.png",(800,600))
By_product={"Boar":116,"Hyena":117,"Deceased":120,"Mummy":120,"Orc_Berserk":120,
            "Orc_Shaman":120,"Orc_Warrior":120}
Enemy_identity={451:"Boar",452:"Deceased",453:"Hyena",454:"Mummy",455:"Orc_Berserk"
                ,456:"Orc_Shaman",457:"Orc_Warrior",458:"Old_man",459:"",460:""}

identity={111:"Mushroom",112:"Mushroom",113:"Mushroom",114:"Mushroom",115:"Mushroom",
          116:"Meat",117:"Meat",118:"Meat",120:"Kit"}
root_path = "J:/Pygame new/"
level_path = "Level1/1-1"
load_level = {"Level1/1-1":"Level11.csv", "Level1/1-2":"Level12.csv"}

bg_data = {"L1B1.png":(8000,600), "L1B2.png":(8000,600), "L1B3.png":(8000,600), "L2B1.png":(8000,600)}
speed_arr=[0.5,0.2]
bgx=[]
bgy=[]
