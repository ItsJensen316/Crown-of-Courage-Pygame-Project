import pygame

class Level_manager:
    def __init__(self):
        self.tiles_arr = []
        self.hero_pos = ()
        self.CheckP = []
        self.Puzzle = []
        self.tiles = []
        self.Slidables = []
        self.Ladder = []
        self.Food = []
        self.Door = []
        self.Lift = []
        self.Boxes = []
        self.Inventory = []
        self.Damage = []
        self.Pushables = []
        self.Danger = []
        self.Rest = []
        self.Floor = []
        self.Enemy = []
        self.Enemies_array = []
        self.level_metadata = {}
        self.current_level = {}
        self.level_path = ""
        self.map = ""
        self.bg_data = {}
        self.bgx = []
        self.bgy = []
        self.bgimages = []
        self.Old_man=[]
        self.Old_man_array = []
        self.x_limit = [0, 0]
        self.y_limit = [0, 0]
    def reset(self):
        self.tiles_arr = []
        self.hero_pos = ()
        self.CheckP = []
        self.Puzzle = []
        self.tiles = []
        self.Slidables = []
        self.Ladder = []
        self.Food = []
        self.Door = []
        self.Lift = []
        self.Boxes = []
        self.Inventory = []
        self.Damage = []
        self.Pushables = []
        self.Danger = []
        self.Rest = []
        self.Floor = []
        self.Enemy = []
        self.Enemies_array = []
        self.level_metadata = {}
        self.current_level = {}
        self.level_path = ""
        self.map = ""
        self.bg_data = {}
        self.bgx = []
        self.bgy = []
        self.bgimages = []
        self.old_man=[]
        self.x_limit = [0, 0]
        self.y_limit = [0, 0]      
