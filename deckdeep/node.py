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

    def __str__(self) -> str:
        return f"Node({self.node_type}, {self.x}, {self.y})"

    def add_child(self, child: "Node"):
        self.children.append(child)

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
            "children": [child.to_dict() for child in self.children],
        }

    @classmethod
    def from_dict(cls, data):
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
        for child_data in data["children"]:
            node.add_child(cls.from_dict(child_data))
        return node
