from typing import List
from deckdeep.monster import Monster
import random
from typing import Dict

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
            
    def decide_action(self, player):
        for monster in self.monsters:
            monster.decide_action(player)

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
            num_monsters = min(1 + level // 2, 3)  # Start with 1 monster, add 1 every 2 levels, max 3
            monsters_to_fight = random.randint(1, num_monsters)
            for _ in range(monsters_to_fight):
                monster_group.add_monster(Monster.generate(level))
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
