import networkx as nx
from collections import OrderedDict

'''
Tasks:
- favor nodes in center over edges
- look for open space
- add attribute has_head to nodes
- target enemy snake heads if enemy smaller
- avoid enemy snake heads if enemy bigger
- optimise
- account for new spaces opening 
- remove nodes more than n spaces away from snakes if evaluating paths less than length n
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
        self.max_path_len = 5
        self.tail_weight = 19.0
        self.snake_weight = 19.0
        self.open_weight = 1.0
        self.food_weight = -5.0

    def update_game(self, game_data):
        self.game_data = game_data
        self.my_length = self.get_snake_length(self.game_data["you"]["body"])
        self.health = self.game_data["you"]["health"]
        self.head = (self.game_data["you"]["body"][0]["x"], self.game_data["you"]["body"][0]["y"])
        self.tail = (self.game_data["you"]["body"][-1]["x"], self.game_data["you"]["body"][-1]["y"])
        self.foods = [(food["x"], food["y"]) for food in self.game_data["board"]["food"]]
        self.update_snakes()
        self.update_food_weight()
        self.update_board()

    def update_snakes(self):
        # clear snakes
        self.snakes = []
        # Add all snakes to self.snakes
        for snake in self.game_data["board"]["snakes"]:
            self.snakes.extend([(point["x"], point["y"]) for point in snake["body"][:]])

    def update_board(self):
        self.board = nx.Graph()
        self.add_nodes()
        self.add_edges()

    def add_nodes(self):
        for y in range(self.board_height):
            for x in range(self.board_width):
                node = (x, y)
                weight = self.open_weight
                if node in self.snakes:
                    weight += self.snake_weight
                if node in self.foods:
                    weight += self.food_weight
                if node == self.tail:
                    weight += self.tail_weight
                self.board.add_node(node, weight=weight)

    def add_edges(self):
        for current_node in self.board.nodes:
            for adj_node in self.get_adjacent(current_node):
                self.board.add_edge(current_node, adj_node)

    def get_move(self):
        print "get move"
        if self.game_data['turn'] == 0:
            return 'up'

        # generate dictionary to hold paths of all lengths <= max_path_len
        all_paths = {}
        for n in range(1, self.max_path_len+2):
            all_paths[n] = []

        # add paths of length n to list of paths with length n in all_paths dictionary
        for node in self.board.nodes:
            try:
                paths = list(nx.all_simple_paths(self.board, source=self.head, target=node, cutoff=self.max_path_len))
                for path in paths:
                    all_paths[len(path)].append(path)
            except nx.NetworkXNoPath:
                continue

        # sort each list of paths in all_paths by lowest weight
        for key in all_paths:
            all_paths[key].sort(key=self.get_avg_weight)

        # return longest path with lowest avg weight
        for key in range(self.max_path_len+1, 1, -1):
            return self.get_direction(all_paths[key][0])

    def get_direction(self, path):
        print "get direction"
        print 'path followed: ', path
        print 'path weight: ', self.get_avg_weight(path)
        print 'node weights: ', [self.board.nodes[node]['weight'] for node in path]
        destination = path[1]

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

    def get_avg_weight(self, path):
        weight_sum = 0
        for node in path:
            weight = self.board.nodes[node]['weight']
            weight_sum += weight
        avg_weight = weight_sum/len(path)
        return avg_weight

    def get_snake_length(self, snake):
        return len(list(OrderedDict.fromkeys([str(point["x"]) + str(point["y"]) for point in snake])))

    def update_food_weight(self):
        return -5 + 0.03*self.health
