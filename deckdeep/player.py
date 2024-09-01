from typing import List
import random
from deckdeep.card import Card, get_player_starting_deck
from typing import Dict, Optional
from deckdeep.status_effect import StatusEffectManager, Bleed
from deckdeep.relic import Relic


class Player:
    def __init__(self, name: str, health: int, symbol: str):
        self.name = name
        self.health = health
        self.max_health = health
        self.shield = 0
        self.bonus_damage = 0
        self.energy = 3
        self.max_energy = 3
        self.symbol = symbol
        self.hand_limit = 7
        self.deck: List[Card] = get_player_starting_deck()
        self.hand: List[Card] = []
        self.discard_pile: List[Card] = []
        self.size = 100
        self.shake = 0
        self.health_gain_on_skip = 5
        self.cards_drawn_per_turn = 5
        self.hp_regain_per_level = 2
        self.status_effects = StatusEffectManager()
        self.relics: List[Relic] = []
        self.strength = 0
        self.dodge_chance = 0
        self.cards_per_turn = 5
        self.phoenix_feather_active = False
        self.extra_turn_chance = 0

    def draw_card(self):
        if not self.deck:
            self.shuffle_deck()
        if self.deck and len(self.hand) < self.hand_limit:
            self.hand.append(self.deck.pop())
        else:
            print("Player hand is full!")

    def shuffle_deck(self):
        self.deck.extend(self.discard_pile)
        self.discard_pile.clear()
        random.shuffle(self.deck)

    def can_play_card(self, card: Card) -> bool:
        return self.energy >= card.energy_cost

    def play_card(self, card: Card, monster_group) -> int:
        score = 0
        if self.can_play_card(card):
            self.bonus_damage += card.bonus_damage
            total_damage = (
                round(card.damage + self.bonus_damage + self.strength)
                if card.damage > 0
                else 0
            )

            if card.targets_all:
                score += monster_group.receive_damage(total_damage)
                for monster in monster_group.monsters:
                    if hasattr(card, "bleed") and card.bleed > 0:
                        monster.status_effects.add_effect(Bleed(card.bleed))
            else:
                target_monster = monster_group.get_selected_monster()
                score += target_monster.receive_damage(total_damage)
                if hasattr(card, "bleed") and card.bleed > 0:
                    target_monster.status_effects.add_effect(Bleed(card.bleed))

            self.heal(round(card.healing))
            self.health -= card.health_cost
            self.shield += card.shield
            self.energy -= card.energy_cost

            for _ in range(card.card_draw):
                self.draw_card()

            self.discard_pile.append(card)
            self.hand.remove(card)
        return score

    def heal(self, amount: int):
        self.health = min(self.max_health, self.health + amount)

    def add_block(self, amount: int):
        self.shield += amount

    def remove_curses(self, amount: int = 1):
        """
        -1 is for all curses to be removed
        """
        for card in self.deck:
            if "Curse" in card.name:
                self.deck.remove(card)
                amount -= 1
            if amount == 0:
                break

    def take_damage(self, damage: int) -> int:
        if random.random() < self.dodge_chance:
            print(f"{self.name} dodged the attack!")
            return 0

        old_health = self.health

        # Handle shield absorption
        if self.shield > 0:
            if damage <= self.shield:
                self.shield -= damage
                damage = 0
            else:
                damage -= self.shield
                self.shield = 0

        # Apply remaining damage to health
        self.health = self.health - damage

        # Phoenix Feather effect
        if self.health <= 0 and self.phoenix_feather_active:
            self.health = 1
            self.phoenix_feather_active = False
            print(f"{self.name} survived with 1 HP thanks to Phoenix Feather!")

        # Calculate actual damage taken
        actual_damage = old_health - self.health

        # Calculate shake based on percentage of max health
        health_percentage = (actual_damage / self.max_health) * 100
        self.shake = round(min(health_percentage, 100))

        return actual_damage

    def end_turn(self):
        self.energy = self.max_energy
        self.bonus_damage = 0
        self.shield = 0
        self.discard_pile.extend(self.hand)
        self.hand.clear()
        for _ in range(self.cards_per_turn):
            self.draw_card()
        self.apply_status_effects()

    def apply_status_effects(self):
        self.status_effects.apply_effects(self)

    def reset_energy(self):
        self.energy = self.max_energy

    def increase_max_energy(
        self,
        level: Optional[int] = None,
        force: bool = False,
    ):
        if level is not None and level % 3 == 0 and self.max_energy < 10:
            print(f"{self.name} gained +1 max energy!")
            self.max_energy += 1
            self.energy = self.max_energy
        elif force:
            print(f"{self.name} gained +1 max energy!")
            self.max_energy += 1
            self.energy = self.max_energy

    def add_card_to_deck(self, card: Card):
        self.deck.append(card)

    def reset_hand(self):
        self.discard_pile.extend(self.hand)
        self.hand.clear()
        for _ in range(self.cards_per_turn):
            self.draw_card()

    def increase_max_health(self, amount: int):
        self.max_health += amount

    def discard_card(self, index: int):
        if 0 <= index < len(self.hand):
            self.discard_pile.append(self.hand.pop(index))

    def add_relic(self, relic: Relic):
        print("Adding New relic", relic.name)
        self.relics.append(relic)

    def to_dict(self) -> Dict:
        base_dict = {
            key: value for key, value in vars(self).items() if not key.startswith("_")
        }
        base_dict["deck"] = [card.to_dict() for card in self.deck]
        base_dict["hand"] = [card.to_dict() for card in self.hand]
        base_dict["discard_pile"] = [card.to_dict() for card in self.discard_pile]
        base_dict["status_effects"] = self.status_effects.to_dict()
        base_dict["relics"] = [relic.to_dict() for relic in self.relics]
        return base_dict

    @classmethod
    def from_dict(cls, data: Dict) -> "Player":
        player = cls(data["name"], data["max_health"], data["symbol"])
        for key, value in data.items():
            if key not in ["deck", "hand", "discard_pile", "status_effects", "relics"]:
                setattr(player, key, value)
        player.deck = [Card.from_dict(card_data) for card_data in data["deck"]]
        player.hand = [Card.from_dict(card_data) for card_data in data["hand"]]
        player.discard_pile = [
            Card.from_dict(card_data) for card_data in data["discard_pile"]
        ]
        player.status_effects = StatusEffectManager.from_dict(data["status_effects"])
        player.relics = [
            Relic.from_dict(relic_data) for relic_data in data.get("relics", [])
        ]
        return player

    def get_sorted_full_deck(self) -> List[Card]:
        full_deck = self.deck + self.hand + self.discard_pile
        return sorted(full_deck, key=lambda card: card.energy_cost)

    def remove_card_from_deck(self, card_index: int) -> Optional[Card]:
        full_deck = self.get_sorted_full_deck()
        if 0 <= card_index < len(full_deck):
            card_to_remove = full_deck[card_index]
            if card_to_remove in self.deck:
                self.deck.remove(card_to_remove)
            elif card_to_remove in self.hand:
                self.hand.remove(card_to_remove)
            elif card_to_remove in self.discard_pile:
                self.discard_pile.remove(card_to_remove)
            return card_to_remove
        return None

    def duplicate_card_in_deck(self, card_index: int) -> Optional[Card]:
        full_deck = self.get_sorted_full_deck()
        if 0 <= card_index < len(full_deck):
            card_to_duplicate = full_deck[card_index]
            new_card = Card(
                name=card_to_duplicate.name,
                energy_cost=card_to_duplicate.energy_cost,
                rarity=card_to_duplicate.rarity,
                damage=card_to_duplicate.damage,
                bonus_damage=card_to_duplicate.bonus_damage,
                healing=card_to_duplicate.healing,
                shield=card_to_duplicate.shield,
                targets_all=card_to_duplicate.targets_all,
                card_draw=card_to_duplicate.card_draw,
                health_cost=card_to_duplicate.health_cost,
                bleed=card_to_duplicate.bleed,
                energy_bonus=card_to_duplicate.energy_bonus,
                health_regain=card_to_duplicate.health_regain,
            )
            # Add the new card to the same pile as the original card
            if card_to_duplicate in self.deck:
                self.deck.append(new_card)
            elif card_to_duplicate in self.hand:
                self.hand.append(new_card)
            elif card_to_duplicate in self.discard_pile:
                self.discard_pile.append(new_card)
            return new_card
        return None
