import networkx as nx
from collections import OrderedDict
import itertools as it


'''
Tasks:
- make board
- add attribute has_snake to nodes
- add attribute has_tail to nodes
- add attribute has_head to nodes
- add attribute has_food to nodes
- weight edges depending on attributes
- neutral weight is 5
- snake weight is 10
- food weight is 1
'''

class Game:
    def __init__(self, game_data):
        self.game_data = {}
        self.board_height = game_data['board']['height']
        self.board_width = game_data['board']['width']
        self.health = 100
        self.my_length = []
        self.head = ("", "")
        self.tail = ("", "")
        self.foods = []
        self.board = nx.Graph()
        self.snakes = []
        self.adj_enemy_head = []
        self.snake_weight = 10
        self.open_weight = 1
        self.food_weight = 0.1
        self.max_path_len = 5

    def update_game(self, game_data):
        self.game_data = game_data
        self.my_length = self.get_snake_length(self.game_data["you"]["body"])
        self.health = self.game_data["you"]["health"]
        self.head = (self.game_data["you"]["body"][0]["x"], self.game_data["you"]["body"][0]["y"])
        self.tail = (self.game_data["you"]["body"][-1]["x"], self.game_data["you"]["body"][-1]["y"])
        self.foods = [(food["x"], food["y"]) for food in self.game_data["board"]["food"]]
        self.update_snakes()
        self.update_board()

    # CHANGE TO MULTIPLE SIMPLE FUNCTIONS
    def update_snakes(self):
        # clear snakes
        self.snakes = []
        # Add all snakes except me to self.snakes
        for snake in self.game_data["board"]["snakes"]:
            if snake["id"] != self.game_data["you"]["id"]:
                self.snakes.extend([(point["x"], point["y"]) for point in snake["body"][:-1]])

        # turn 0, 1 edge cases don't add me
        if self.game_data["turn"] == 0 or self.game_data["turn"] == 1:
            return

        # add my body without head and tail to self.snakes
        self.snakes.extend([(point["x"], point["y"]) for point in self.game_data["you"]["body"][1:-1]])

    def update_board(self):
        self.board = nx.Graph()
        for y in range(self.board_height):
            for x in range(self.board_width):
                current_node = (x, y)

                # add attribute has_snake
                if current_node in self.snakes:
                    self.board.add_node(current_node, has_snake=True, my_tail=False)

                # add attribute my_tail
                if current_node == self.tail:
                    self.board.add_node(current_node, has_snake=True, my_tail=True)

                else:
                    self.board.add_node(current_node, has_snake=False, my_tail=False)

                # add edges to node
                self.add_edges(current_node)

    def add_edges(self, current_node):
        for adj_node in self.get_adjacent(current_node):

            # don't add head or tail if my length is 2
            if self.my_length == 2:
                if (current_node not in [self.head, self.tail]) or (adj_node not in [self.head, self.tail]):
                    self.board.add_edge(adj_node, current_node, weight=self.open_weight)

            # node has snake
            elif self.board.nodes[adj_node]['has_snake']:
                self.board.add_edge(adj_node, current_node, weight=self.snake_weight)

            # open space
            else:
                self.board.add_edge(adj_node, current_node, weight=self.open_weight)

    def get_move(self):
        print "get move"
        all_paths = []

        # add every path to all_paths
        for node in self.board.nodes:
            try:
                all_paths.append(nx.all_simple_paths(self.board, self.head, node, cutoff=self.max_path_len))
            except nx.NetworkXNoPath:
                continue

        # sort all_paths by lowest average weight
        all_paths.sort(key=self.get_avg_weight)

        # return path with lowest avg weight
        return self.get_direction(all_paths[0])

    def get_direction(self, path):
        print "get direction"
        destination = [next(path), next(path)]
        # return direction to node
        if self.head[0] == destination[0]:
            if self.head[1] > destination[1]:
                return 'up'
            return 'down'
        if self.head[0] > destination[0]:
            return 'left'
        return 'right'

    def get_adjacent(self, current_node):
        x = current_node[0]
        y = current_node[1]
        adj_nodes = []
        adj_nodes.extend(node for node in [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)] if self.board.has_node(node))
        return adj_nodes

    def get_avg_weight(self, all_paths):
        total_weight = 0
        for path in all_paths:
            if len(path) < 2:
                continue
            for i in range(1, len(path)):
                node = path[i-1]
                next_node = path[i]
                total_weight += self.board.edges[node, next_node]['weight']
            return total_weight/len(path)

    def get_snake_length(self, snake):
        return len(list(OrderedDict.fromkeys([str(point["x"]) + str(point["y"]) for point in snake])))
