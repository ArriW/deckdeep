import random
from typing import List, Optional, Tuple
from deckdeep.node import Node, NodeType

class MapGenerator:
    def __init__(self):
        self.width = 6
        self.height = 15
        self.path_count = 6
        self.map: List[List[Optional[Node]]] = []

    def generate_map(self) -> List[List[Optional[Node]]]:
        self.map = [[None for _ in range(self.width)] for _ in range(self.height)]
        self._generate_paths()
        self._trim_paths()
        self._trim_unreachable_nodes()
        self._assign_node_types()
        self._create_boss_node()
        self._connect_nodes()
        return self.map

    def _generate_paths(self):
        for _ in range(self.path_count):
            start_x = random.randint(0, self.width - 1)
            self._create_path(start_x)

    def _create_path(self, start_x: int):
        x, y = start_x, 0
        while y < self.height - 1:  # Stop before the boss row
            if self.map[y][x] is None:
                self.map[y][x] = Node(NodeType.MONSTER, x, y)
            
            next_positions = self._get_valid_next_positions(x, y)
            if not next_positions:
                break  # No valid moves, end the path

            x, y = random.choice(next_positions)

    def _get_valid_next_positions(self, x: int, y: int) -> List[Tuple[int, int]]:
        valid_positions = []
        for dx in [-1, 0, 1]:
            next_x = x + dx
            next_y = y + 1
            if 0 <= next_x < self.width and next_y < self.height - 1:
                if self.map[next_y][next_x] is None and not self._path_crosses(x, y, next_x, next_y):
                    valid_positions.append((next_x, next_y))
        return valid_positions

    def _path_crosses(self, x1: int, y1: int, x2: int, y2: int) -> bool:
        if abs(x2 - x1) == 1:
            if self.map[y1][x2] is not None and self.map[y2][x1] is not None:
                return True
        return False

    def _trim_paths(self):
        # Ensure only one node remains in the center of the first row
        center = self.width // 2
        for x in range(self.width):
            if x != center:
                self.map[0][x] = None

        # If the center node is None, create one
        if self.map[0][center] is None:
            self.map[0][center] = Node(NodeType.MONSTER, center, 0)

        # Trim the paths to connect to the center node
        for y in range(1, self.height - 1):
            for x in range(self.width):
                if self.map[y][x] is not None:
                    if not self._has_connection_to_start(x, y):
                        self.map[y][x] = None

    def _has_connection_to_start(self, x: int, y: int) -> bool:
        if y == 0:
            return x == self.width // 2
        for dx in [-1, 0, 1]:
            prev_x = x + dx
            if 0 <= prev_x < self.width and self.map[y-1][prev_x] is not None:
                if self._has_connection_to_start(prev_x, y-1):
                    return True
        return False

    def _trim_unreachable_nodes(self):
        reachable = set()
        self._dfs(self.width // 2, 0, reachable)
        
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) not in reachable:
                    self.map[y][x] = None

    def _dfs(self, x: int, y: int, visited: set):
        if (x, y) in visited or self.map[y][x] is None:
            return
        visited.add((x, y))
        for dx, dy in [(-1, 1), (0, 1), (1, 1)]:
            next_x, next_y = x + dx, y + dy
            if 0 <= next_x < self.width and next_y < self.height:
                self._dfs(next_x, next_y, visited)

    def _assign_node_types(self):
        for y in range(self.height - 1):  # Exclude the boss row
            for x in range(self.width):
                node = self.map[y][x]
                if node is not None:
                    if y < 3:
                        node.node_type = NodeType.MONSTER
                    elif y < 6:
                        node.node_type = random.choice([NodeType.MONSTER, NodeType.EVENT])
                    elif y < 9:
                        node.node_type = random.choice([NodeType.MONSTER, NodeType.EVENT, NodeType.ELITE])
                    elif y < 12:
                        node.node_type = random.choice([NodeType.MONSTER, NodeType.EVENT, NodeType.ELITE, NodeType.REST])
                    else:
                        node.node_type = random.choice([NodeType.MONSTER, NodeType.EVENT, NodeType.ELITE, NodeType.REST, NodeType.TREASURE])

    def _create_boss_node(self):
        boss_x = self.width // 2
        self.map[self.height - 1][boss_x] = Node(NodeType.BOSS, boss_x, self.height - 1)
        self._connect_boss_to_previous_row()

    def _connect_boss_to_previous_row(self):
        boss_node = self.map[self.height - 1][self.width // 2]
        previous_row = self.height - 2
        for x in range(self.width):
            if self.map[previous_row][x] is not None:
                self.map[previous_row][x].add_child(boss_node)
                # The add_child method now handles both child and parent relationships

    def _connect_nodes(self):
        for y in range(self.height - 1):
            for x in range(self.width):
                if self.map[y][x] is not None:
                    # Try to connect to nodes in the next row
                    for dx in [0, -1, 1]:  # Prioritize straight connections
                        next_x = x + dx
                        if 0 <= next_x < self.width and self.map[y+1][next_x] is not None:
                            if self.map[y][x].can_connect(self.map[y+1][next_x]):
                                self.map[y][x].add_child(self.map[y+1][next_x])
                                if self.map[y][x].children:
                                    break  # Stop after first successful connection

        # Ensure all nodes (except the first row) have at least one parent
        for y in range(1, self.height):
            for x in range(self.width):
                if self.map[y][x] is not None and not self.map[y][x].parents:
                    for dx in [0, -1, 1]:  # Prioritize straight connections
                        prev_x = x + dx
                        if 0 <= prev_x < self.width and self.map[y-1][prev_x] is not None:
                            if self.map[y-1][prev_x].can_connect(self.map[y][x]):
                                self.map[y-1][prev_x].add_child(self.map[y][x])
                                if self.map[y][x].parents:
                                    break  # Stop after first successful connection

        # Final check: ensure all nodes (except boss) have at least one child
        for y in range(self.height - 1):
            for x in range(self.width):
                if self.map[y][x] is not None and not self.map[y][x].children:
                    for dx in [0, -1, 1]:  # Prioritize straight connections
                        next_x = x + dx
                        if 0 <= next_x < self.width and self.map[y+1][next_x] is not None:
                            if self.map[y][x].can_connect(self.map[y+1][next_x]):
                                self.map[y][x].add_child(self.map[y+1][next_x])
                                if self.map[y][x].children:
                                    break  # Stop after first successful connection

        # Connect all nodes in the second-to-last row to the boss node
        boss_node = self.map[self.height - 1][self.width // 2]
        for x in range(self.width):
            if self.map[self.height - 2][x] is not None:
                self.map[self.height - 2][x].add_child(boss_node)
                boss_node.add_parent(self.map[self.height - 2][x])

        # Ensure the boss node is connected to at least one node in the second-to-last row
        if not boss_node.parents:
            for x in range(self.width):
                if self.map[self.height - 2][x] is not None:
                    self.map[self.height - 2][x].add_child(boss_node)
                    boss_node.add_parent(self.map[self.height - 2][x])
                    break

    def _would_create_intersection(self, x1, y1, x2, y2):
        # Check if there's already a connection that would intersect with this one
        dx = x2 - x1
        if dx == 0:
            return False  # Vertical connections can't intersect
        
        # Check the node between the two we're trying to connect
        mid_x, mid_y = x1 + dx // 2, y1 + 1
        
        # If there's no node in between, there can't be an intersection
        if self.map[mid_y][mid_x] is None:
            return False
        
        # Check if the middle node has connections that would intersect
        middle_node = self.map[mid_y][mid_x]
        for child in middle_node.children:
            if (child.x < mid_x and x2 > mid_x) or (child.x > mid_x and x2 < mid_x):
                return True
        
        return False

    def print_map(self):
        for row in self.map:
            print(" ".join(["B" if node and node.node_type == NodeType.BOSS else "O" if node else "." for node in row]))

    def get_start_node(self) -> Node:
        return self.map[0][self.width // 2]

