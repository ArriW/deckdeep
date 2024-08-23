from typing import List
import random
from deckdeep.card import Card, player_starting_deck
from typing import Dict

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
        self.deck: List[Card] = player_starting_deck.copy()  # Use .copy() to avoid modifying the original
        self.hand: List[Card] = []
        self.discard_pile: List[Card] = []
        self.size = 100
        self.shake = 0
        self.health_gain_on_skip = 5
        self.cards_drawn_per_turn = 5
        self.hp_regain_per_level = 2

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
            total_damage = round(card.damage + self.bonus_damage) if card.damage > 0 else 0
            
            if card.targets_all:
                score += monster_group.receive_damage(total_damage)
            else:
                score += monster_group.get_selected_monster().receive_damage(total_damage)
            
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

    def take_damage(self, damage: int) -> int:
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
        self.health = max(0, self.health - damage)
    
        # Calculate actual damage taken
        actual_damage = old_health - self.health
    
        # Calculate shake based on percentage of max health
        health_percentage = (actual_damage / self.max_health) * 100
        self.shake = round(min(health_percentage, 100))
    
        return self.health

    def end_turn(self):
        self.energy = self.max_energy
        self.bonus_damage = 0
        self.discard_pile.extend(self.hand)
        self.hand.clear()
        for _ in range(self.cards_drawn_per_turn):
            self.draw_card()

    def reset_energy(self):
        self.energy = self.max_energy

    def increase_max_energy(self):
        self.max_energy += 1

    def add_card_to_deck(self, card: Card):
        self.deck.append(card)

    def reset_hand(self):
        self.discard_pile.extend(self.hand)
        self.hand.clear()
        for _ in range(self.cards_drawn_per_turn):
            self.draw_card()

    def increase_max_health(self, amount: int):
        self.max_health += amount

    def discard_card(self, index: int):
        if 0 <= index < len(self.hand):
            self.discard_pile.append(self.hand.pop(index))

    def to_dict(self) -> Dict:
            base_dict = {key: value for key, value in vars(self).items() if not key.startswith('_')}
            base_dict['deck'] = [card.to_dict() for card in self.deck]
            base_dict['hand'] = [card.to_dict() for card in self.hand]
            base_dict['discard_pile'] = [card.to_dict() for card in self.discard_pile]
            return base_dict

    @classmethod
    def from_dict(cls, data: Dict) -> 'Player':
        player = cls(data["name"], data["max_health"], data["symbol"])
        for key, value in data.items():
            if key not in ['deck', 'hand', 'discard_pile']:
                setattr(player, key, value)
        player.deck = [Card.from_dict(card_data) for card_data in data["deck"]]
        player.hand = [Card.from_dict(card_data) for card_data in data["hand"]]
        player.discard_pile = [Card.from_dict(card_data) for card_data in data["discard_pile"]]
        return player