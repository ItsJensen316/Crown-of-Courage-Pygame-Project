class Level_manager:
    def __init__(self):
        self.reset()

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
        self.Button = []
        self.Enemies_array = []
        self.level_metadata = {}
        self.level_path = ""
        self.map = ""
        self.bg_data = {}
        self.bgx = []
        self.bgy = []
        self.bgimages = []
        self.Old_man = []
        self.Old_man_array = []
        self.x_limit = [0, 0]
        self.y_limit = [0, 0]
