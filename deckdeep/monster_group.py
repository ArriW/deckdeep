from typing import List, Tuple, Optional
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
        try:
            return random.choice(self.monsters)
        except IndexError:
            return None

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
    def generate(level: int, is_boss: bool = False, boss_type: Optional[str] = None) -> Tuple["MonsterGroup", float, float]:
        monster_group = MonsterGroup()

        def scaling_factor(lvl):
            return 1 + math.log(lvl + 1, 2)  # Logarithmic scaling

        base_power = 15
        target_power = base_power * scaling_factor(level)
        target_power *= random.uniform(0.9, 1.1)

        current_power = 0
        max_monsters = 5

        boss_groups = {
            "corrupted_paladin": ["Guardian_1", "Guardian_1"],
            "troll_king": ["goblin_1", "goblin_1"],
            "dragon_1": [],
        }

        if is_boss:
            boss = Monster.generate(level, is_boss=True)
            monster_group.add_monster(boss)
            
            for minion_type in boss_groups.get(boss.name, []):
                minion = Monster.generate(max(level-10,2), monster_type=minion_type)
                monster_group.add_monster(minion)
            return monster_group, target_power, monster_group.get_power_rating()
        else:
            attempts = 0
            while current_power < target_power and len(monster_group.monsters) < max_monsters:
                new_monster = Monster.generate(level)
                if current_power + new_monster.power_rating > target_power * 1.2 and attempts < 5:
                    continue
                monster_group.add_monster(new_monster)
                current_power += new_monster.power_rating

            actual_power = monster_group.get_power_rating()
        return monster_group, target_power, actual_power

    def to_dict(self) -> Dict:
        return {
            "monsters": [monster.to_dict() for monster in self.monsters],
            "selected_index": self.selected_index,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "MonsterGroup":
        monster_group = cls()
        monster_group.monsters = [
            Monster.from_dict(monster_data) for monster_data in data["monsters"]
        ]
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
