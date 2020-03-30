import networkx as nx
from collections import OrderedDict

'''
Tasks:
- add attribute has_head to nodes
- limit scope and optimise
- look ahead
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
        self.tail_weight = -1.0
        self.snake_weight = 10.0
        self.open_weight = 1.0
        self.food_weight = -5.0
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

        # add my body to self.snakes
        self.snakes.extend([(point["x"], point["y"]) for point in self.game_data["you"]["body"][1:]])

    def update_board(self):
        self.board = nx.Graph()
        self.add_nodes()
        self.add_edges()

    def add_nodes(self):
        for y in range(self.board_height):
            for x in range(self.board_width):
                self.board.add_node((x, y), has_snake=False, my_tail=False, has_food=False)

        # add attribute has_snake
        for node in self.snakes:
            self.board.nodes[node]['has_snake'] = True

        # add attribute has food
        for node in self.foods:
            self.board.nodes[node]['has_food'] = True

        # add attribute my_tail
        self.board.nodes[self.tail]['my_tail'] = True

    def add_edges(self):
        for current_node in self.board.nodes:
            for adj_node in self.get_adjacent(current_node):

                # don't add edge from head to tail if my length is 2
                if self.my_length == 2:
                    if (current_node not in [self.head, self.tail]) or (adj_node not in [self.head, self.tail]):
                        self.board.add_edge(current_node, adj_node, weight=self.open_weight)

                # has snake
                elif self.board.nodes[current_node]['has_snake']:
                    self.board.add_edge(current_node, adj_node, weight=self.snake_weight)

                # has food
                elif self.board.nodes[current_node]['has_food']:
                    self.board.add_edge(current_node, adj_node, weight=self.food_weight)

                # open space
                elif adj_node not in self.snakes:
                    self.board.add_edge(current_node, adj_node, weight=self.open_weight)

    def get_move(self):
        print "get move"
        if self.game_data['turn'] == 0:
            return 'up'

        all_paths = []
        # add every path to all_paths
        for node in self.board.nodes:
            try:
                paths = list(nx.all_simple_paths(self.board, source=self.head, target=node, cutoff=self.max_path_len))
                for path in paths:
                    all_paths.append(path)
            except nx.NetworkXNoPath:
                continue

        # sort all_paths by lowest weight
        all_paths.sort(key=self.get_avg_weight)

        # return path with lowest avg weight
        return self.get_direction(all_paths[0])

    def get_direction(self, path):
        print "get direction"
        print 'path followed: ', path
        print 'path weight: ', self.get_avg_weight(path)
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
        for edge in nx.utils.pairwise(path):
            weight = self.board.edges[edge]['weight']
            weight_sum += weight
        avg_weight = weight_sum/len(path)
        return avg_weight

    def get_snake_length(self, snake):
        return len(list(OrderedDict.fromkeys([str(point["x"]) + str(point["y"]) for point in snake])))
