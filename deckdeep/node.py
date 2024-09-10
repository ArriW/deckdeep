from typing import List, Optional
from enum import Enum
from deckdeep.monster_group import MonsterGroup


class NodeType(Enum):
    START = "start"
    MONSTER = "monster"
    TREASURE = "treasure"
    REST = "rest"
    EVENT = "event"
    ELITE = "elite"
    BOSS = "boss"


class Node:
    def __init__(
        self,
        node_type: NodeType,
        x: int,
        y: int,
        content: Optional[dict] = None,
    ):
        self.node_type = node_type
        self.x = x
        self.y = y
        self.content = content or {}
        self.children: List["Node"] = []
        self.parents: List["Node"] = []  # Add this line

    def __str__(self) -> str:
        return f"Node({self.node_type}, {self.x}, {self.y})"

    def would_create_intersection(self, other: "Node") -> bool:
        # Check if connecting to this node would create an intersection
        if abs(self.x - other.x) <= 1 or self.y == other.y:
            return False  # No intersection for adjacent or same-row nodes
        for child in self.children:
            if (child.x < other.x and self.x > other.x) or (child.x > other.x and self.x < other.x):
                return True
        return False

    def can_connect(self, other: "Node") -> bool:
        # Allow connections to the boss node without restrictions
        if other.node_type == NodeType.BOSS:
            return True
        # For other nodes, use the existing logic
        return (
            abs(self.x - other.x) <= 1
            and other.y == self.y + 1
            and not self.would_create_intersection(other)
        )

    def add_child(self, child: "Node"):
        if child not in self.children:
            self.children.append(child)
            if self not in child.parents:
                child.parents.append(self)

    def add_parent(self, parent: "Node"):
        if parent not in self.parents:
            self.parents.append(parent)
            if self not in parent.children:
                parent.children.append(self)

    def to_dict(self):
        content_dict = self.content.copy()
        if "monsters" in content_dict and isinstance(
            content_dict["monsters"], MonsterGroup
        ):
            content_dict["monsters"] = content_dict["monsters"].to_dict()
        if "event" in content_dict:
            content_dict["event"] = content_dict["event"].__class__.__name__
        return {
            "node_type": self.node_type.value,
            "x": self.x,
            "y": self.y,
            "content": content_dict,
            "children": [{"x": child.x, "y": child.y} for child in self.children],
            "parents": [{"x": parent.x, "y": parent.y} for parent in self.parents],
        }

    @classmethod
    def from_dict(cls, data, node_map=None):
        node = cls(
            NodeType(data["node_type"]),
            data["x"],
            data["y"],
            data["content"],
        )
        if "monsters" in node.content and isinstance(node.content["monsters"], dict):
            node.content["monsters"] = MonsterGroup.from_dict(node.content["monsters"])
        if "event" in node.content and isinstance(node.content["event"], str):
            event_class = globals()[node.content["event"]]
            node.content["event"] = event_class()
        
        if node_map:
            for child_data in data["children"]:
                child_node = node_map[child_data["y"]][child_data["x"]]
                if child_node:
                    node.add_child(child_node)
            for parent_data in data["parents"]:
                parent_node = node_map[parent_data["y"]][parent_data["x"]]
                if parent_node:
                    node.add_parent(parent_node)
        
        return node
