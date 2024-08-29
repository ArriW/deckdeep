from typing import List, Tuple
from deckdeep.monster import Monster
import random
from typing import Dict
import math

class MonsterGroup:
    def __init__(self):
        self.monsters: List[Monster] = []
        self.selected_index = 0

    def __str__(self):
        return ", ".join([str(monster) for monster in self.monsters])

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

    def get_power_rating(self) -> int:
        return sum([monster.calculate_power_rating() for monster in self.monsters])
    
    def select_previous(self):
        self.monsters[self.selected_index].selected = False
        self.selected_index = (self.selected_index - 1) % len(self.monsters)
        self.monsters[self.selected_index].selected = True

    def get_selected_monster(self) -> Monster:
        return self.monsters[self.selected_index]

    def remove_dead_monsters(self):
        self.monsters = [monster for monster in self.monsters if monster.is_alive()]
        if self.monsters:
            self.selected_index = min(self.selected_index, len(self.monsters) - 1)
            self.monsters[self.selected_index].selected = True

    def attack(self, player):
        for monster in self.monsters:
            monster.attack(player)

    def decide_action(self, player) -> List[str]:
            return [monster.decide_action(player) for monster in self.monsters]

    def receive_damage(self, damage: int) -> int:
        total_damage_dealt = 0
        for monster in self.monsters:
            total_damage_dealt += monster.receive_damage(damage)
        return total_damage_dealt

    def get_total_monster_power(self) -> int:
        return sum(monster.power_rating for monster in self.monsters)

    @staticmethod
    def generate(level: int, is_boss: bool = False) -> Tuple['MonsterGroup', float, float]:
        monster_group = MonsterGroup()
    
        # Adjusted scaling function
        def scaling_factor(lvl):
            return 1 + math.log(lvl + 1, 2)  # Logarithmic scaling

        base_power = 20
        target_power = base_power * scaling_factor(level)
    
        # Add a small amount of randomness (±10%)
        target_power *= random.uniform(0.9, 1.1)

        current_power = 0
        max_monsters = 5
        if is_boss:
            boss = Monster.generate(level,is_boss=True)
            monster_group.add_monster(boss)
            return monster_group , target_power, boss.power_rating
        else: 
            while current_power < target_power and len(monster_group.monsters) < max_monsters:
                new_monster = Monster.generate(level)
                monster_group.add_monster(new_monster)
                current_power += new_monster.power_rating

            # Add elite monster with a certain probability
            if random.random() < 0.15 and len(monster_group.monsters) < max_monsters:
                elite_level = min(level + 2, int(level * 1.3))
                elite_monster = Monster.generate(elite_level)
                monster_group.add_monster(elite_monster)

            actual_power = monster_group.get_power_rating()
        return monster_group, target_power, actual_power

    def to_dict(self) -> Dict:
        return {
            "monsters": [monster.to_dict() for monster in self.monsters],
            "selected_index": self.selected_index
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'MonsterGroup':
        monster_group = cls()
        monster_group.monsters = [Monster.from_dict(monster_data) for monster_data in data["monsters"]]
        monster_group.selected_index = data["selected_index"]
        return monster_group

    def apply_status_effects(self):
        for monster in self.monsters:
            monster.apply_status_effects()

    def execute_actions(self, player):
        results = []
        for monster in self.monsters:
            if monster.is_alive():
                result = monster.execute_action(monster.intention, player)
                results.append(result)
        return results