from typing import List
from deckdeep.monster import Monster
import random
from typing import Dict
import math

class MonsterGroup:
    def __init__(self):
        self.monsters: List[Monster] = []
        self.selected_index = 0

    def __str__(self):
        return ",".join([str(monster) for monster in self.monsters])

    def add_monster(self, monster: Monster):
        self.monsters.append(monster)
        if len(self.monsters) == 1:
            monster.selected = True

    def select_next(self):
        self.monsters[self.selected_index].selected = False
        self.selected_index = (self.selected_index + 1) % len(self.monsters)
        self.monsters[self.selected_index].selected = True

    def random_monster(self) -> Monster:
        return random.choice(self.monsters)
    
    def select_previous(self):
        self.monsters[self.selected_index].selected = False
        self.selected_index = (self.selected_index - 1) % len(self.monsters)
        self.monsters[self.selected_index].selected = True

    def get_selected_monster(self) -> Monster:
        return self.monsters[self.selected_index]

    def remove_dead_monsters(self):
        self.monsters = [monster for monster in self.monsters if monster.health > 0]
        if self.monsters:
            self.selected_index = min(self.selected_index, len(self.monsters) - 1)
            self.monsters[self.selected_index].selected = True

    def attack(self, player):
        for monster in self.monsters:
            monster.attack(player)
            
    def decide_action(self, player) -> List[str]:
        intentions = []
        for monster in self.monsters:
            intention = monster.decide_action(player)
            intentions.append(intention)
        return intentions

    def receive_damage(self, damage: int) -> int:
        score = 0
        for monster in self.monsters:
            score += monster.receive_damage(damage)
        return score

    def get_total_monster_power(self) -> int:
        return sum([monster.get_power() for monster in self.monsters])

    @staticmethod
    def generate(level: int, is_boss: bool = False):
        monster_group = MonsterGroup()
        if is_boss:
            monster_group.add_monster(Monster.generate_boss(level))
        else:
            target_power = math.log(level + 1, 1.5) * 100  # Adjust the base and multiplier as needed
            current_power = 0
            max_monsters = min(5, 1 + level // 5)  # Cap at 5 monsters, increase max every 5 levels

            while current_power < target_power and len(monster_group.monsters) < max_monsters:
                new_monster = Monster.generate(level)
                monster_group.add_monster(new_monster)
                current_power += new_monster.power_rating

        return monster_group

    def to_dict(self) -> Dict:
        return {
            "monsters": [monster.to_dict() for monster in self.monsters],
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'MonsterGroup':
        monster_group = cls()
        monster_group.monsters = [Monster.from_dict(monster_data) for monster_data in data["monsters"]]
        return monster_group
