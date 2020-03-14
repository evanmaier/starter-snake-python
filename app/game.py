import networkx as nx
import random

'''
Tasks:
- test
- game class
- make board
'''

class Game:
    def __init__(self, game_data):
        self.game_data = {}
        self.board_height = game_data['board']['height']
        self.board_width = game_data['board']['width']
        self.health = 100
        self.head = ("", "")
        self.tail = ("", "")
        self.foods = []

    def update_game(self, game_data):
        self.game_data = game_data
        self.health = self.game_data["you"]["health"]
        self.head = (self.game_data["you"]["body"][0]["x"], self.game_data["you"]["body"][0]["y"])
        self.tail = (self.game_data["you"]["body"][-1]["x"], self.game_data["you"]["body"][-1]["y"])
        self.foods = [(food["x"], food["y"]) for food in self.game_data["board"]["food"]]

    def get_move(self):
        print "get move"
        return self.get_direction()

    def get_direction(self):
        print "get direction"
        directions = ['up', 'down', 'left', 'right']
        direction = random.choice(directions)
        return direction