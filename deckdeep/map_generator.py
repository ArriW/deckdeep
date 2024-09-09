import random
from enum import Enum
from typing import List, Optional
from deckdeep.node import Node, NodeType


class MapGenerator:
    def __init__(self):
        self.width = 7
        self.height = 15
        self.map: List[List[Optional[Node]]] = [
            [None for _ in range(self.width)] for _ in range(self.height)
        ]

    def generate_map(self) -> List[List[Optional[Node]]]:
        self._generate_paths()
        self._assign_node_types()
        self._connect_nodes()

        # Ensure there's at least one node in the bottom row
        if not any(self.map[0]):
            self.map[0][self.width // 2] = Node(NodeType.START, self.width // 2, 0)

        return self.map

    def _generate_paths(self):
        # Generate 6 paths from bottom to top
        for _ in range(6):
            x = random.randint(0, self.width - 1)
            y = 0
            while y < self.height - 1:
                if self.map[y][x] is None:
                    self.map[y][x] = Node(NodeType.MONSTER, x, y)  # Temporary type
                y += 1
                x += random.choice([-1, 0, 1])
                x = max(0, min(x, self.width - 1))

    def _assign_node_types(self):
        # Assign node types based on the rules
        for y in range(self.height):
            for x in range(self.width):
                if self.map[y][x] is not None:
                    if y == 0:
                        self.map[y][x].node_type = NodeType.MONSTER
                    elif y == self.height - 1:
                        self.map[y][x].node_type = NodeType.REST
                    elif y == self.height - 2:
                        self.map[y][x].node_type = NodeType.TREASURE
                    else:
                        self.map[y][x].node_type = random.choices(
                            [
                                NodeType.MONSTER,
                                NodeType.EVENT,
                                NodeType.ELITE,
                                NodeType.REST,
                            ],
                            weights=[0.65, 0.2, 0.1, 0.05],
                        )[0]

    def _connect_nodes(self):
        for y in range(self.height - 1):
            for x in range(self.width):
                if self.map[y][x] is not None:
                    for dx in [-1, 0, 1]:
                        nx = x + dx
                        if 0 <= nx < self.width and self.map[y + 1][nx] is not None:
                            self.map[y][x].add_child(self.map[y + 1][nx])

        # Add boss node at the top
        boss_node = Node(NodeType.BOSS, self.width // 2, self.height)
        for x in range(self.width):
            if self.map[self.height - 1][x] is not None:
                self.map[self.height - 1][x].add_child(boss_node)
