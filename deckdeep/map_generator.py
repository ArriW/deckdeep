import random
from enum import Enum
from typing import List, Optional
from deckdeep.node import Node, NodeType


import random
from typing import List, Optional
from deckdeep.node import Node, NodeType

class MapGenerator:
    def __init__(self):
        self.width = 7
        self.height = 15
        self.map: List[List[Optional[Node]]] = []

    def generate_map(self) -> List[List[Optional[Node]]]:
        self.map = [[None for _ in range(self.width)] for _ in range(self.height)]
        self._generate_paths()
        self._assign_node_types()
        self._connect_nodes()
        return self.map

    def _generate_paths(self):
        # Ensure there's always a node at the bottom center
        self.map[0][self.width // 2] = Node(NodeType.MONSTER, self.width // 2, 0)

        # Generate 3-5 paths from bottom to top
        for _ in range(random.randint(3, 5)):
            x = random.randint(0, self.width - 1)
            y = 1  # Start from y=1 since we've already placed a node at y=0
            while y < self.height:
                if self.map[y][x] is None:
                    self.map[y][x] = Node(NodeType.MONSTER, x, y)  # Temporary type
                y += 1
                x += random.choice([-1, 0, 1])
                x = max(0, min(x, self.width - 1))

    def _assign_node_types(self):
        for y in range(self.height):
            for x in range(self.width):
                if self.map[y][x] is not None:
                    if y == 0:
                        self.map[y][x].node_type = NodeType.MONSTER
                    elif y == self.height - 1:
                        self.map[y][x].node_type = NodeType.BOSS
                    else:
                        self.map[y][x].node_type = random.choices(
                            [NodeType.MONSTER, NodeType.EVENT, NodeType.ELITE, NodeType.REST, NodeType.TREASURE],
                            weights=[0.5, 0.2, 0.1, 0.1, 0.1],
                        )[0]

    def _connect_nodes(self):
        for y in range(self.height - 1):
            for x in range(self.width):
                if self.map[y][x] is not None:
                    for dx in [-1, 0, 1]:
                        nx = x + dx
                        if 0 <= nx < self.width and self.map[y + 1][nx] is not None:
                            self.map[y][x].add_child(self.map[y + 1][nx])

        # Ensure the bottom node is connected to at least one node above it
        bottom_node = self.map[0][self.width // 2]
        if not bottom_node.children:
            for x in range(self.width):
                if self.map[1][x] is not None:
                    bottom_node.add_child(self.map[1][x])
                    break

        # If still no children, create a new node above and connect it
        if not bottom_node.children:
            new_node = Node(NodeType.MONSTER, self.width // 2, 1)
            self.map[1][self.width // 2] = new_node
            bottom_node.add_child(new_node)

    def print_map(self):
        for row in self.map:
            print(' '.join(['O' if node else '.' for node in row]))
