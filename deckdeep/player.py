from typing import List
import random
from deckdeep.card import Card, get_player_starting_deck
from typing import Dict, Optional
from deckdeep.status_effect import StatusEffectManager, Bleed, Weakness, Bolster, Burn
from deckdeep.relic import Relic
from deckdeep.relic import TriggerWhen


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
        self.applied_permanent_effects: Dict[str, Set[str]] = {}
        self.is_dying = False
        self.death_start_time = 0

    def add_applied_permanent_effect(self, effect_name: str, relic_id: str):
        if effect_name not in self.applied_permanent_effects:
            self.applied_permanent_effects[effect_name] = set()
        self.applied_permanent_effects[effect_name].add(relic_id)

    def has_applied_permanent_effect(self, effect_name: str, relic_id: str) -> bool:
        return (effect_name in self.applied_permanent_effects and 
                relic_id in self.applied_permanent_effects[effect_name])

    def add_relic(self, relic: Relic) -> str:
        msg = f"Adding new relic {relic.name}"
        
        # Reset the application status for the new relic
        relic.reset_application_status()
        
        # Always add the new relic instance
        self.relics.append(relic)
        
        # Always apply the effect for new relics, regardless of whether it's a duplicate
        if relic.trigger_when == TriggerWhen.PERMANENT:
            msg += ". " + relic.apply_effect(self, None)
        
        return msg

    def apply_relic_effects(self, trigger: TriggerWhen) -> str:
        msg = ""
        for relic in self.relics:
            if relic.trigger_when == trigger:
                msg += relic.apply_effect(self, None) + " "
        return msg.strip()

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
            total_damage = card.calculate_total_damage(self.bonus_damage, self.strength)

            for _ in range(card.num_attacks):
                if card.targets_all:
                    score += monster_group.receive_damage(total_damage // card.num_attacks)
                    for monster in monster_group.monsters:
                        self.apply_card_effects(card, monster)
                else:
                    target_monster = monster_group.get_selected_monster()
                    if target_monster is None:
                        continue
                    score += target_monster.receive_damage(total_damage // card.num_attacks)
                    self.apply_card_effects(card, target_monster)

            # Apply Bolster to the player
            if hasattr(card, "bolster") and card.bolster > 0:
                self.status_effects.add_effect(Bolster(card.bolster))

            self.heal(round(card.healing))
            self.health -= card.health_cost
            self.shield += card.shield
            self.energy -= card.energy_cost

            for _ in range(card.card_draw):
                self.draw_card()

            self.discard_pile.append(card)
            self.hand.remove(card)
        return score

    def apply_card_effects(self, card: Card, monster):
        if hasattr(card, "bleed") and card.bleed > 0:
            monster.status_effects.add_effect(Bleed(card.bleed))
        if hasattr(card, "weakness") and card.weakness > 0:
            monster.status_effects.add_effect(Weakness(card.weakness))
        if hasattr(card, "burn") and card.burn > 0:
            monster.status_effects.add_effect(Burn(card.burn))

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

        # Apply Bolster effect
        bolster_effect = next((effect for effect in self.status_effects.effects if isinstance(effect, Bolster)), None)
        if bolster_effect:
            damage = max(0, damage - bolster_effect.value)

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
        if level is not None and level % 5 == 0 and self.max_energy < 10:
            print(f"{self.name} gained +1 max energy!")
            self.max_energy += 1
            self.energy = self.max_energy
        elif force:
            print(f"{self.name} gained +1 max energy!")
            self.max_energy += 1
            self.energy = self.max_energy

    def increase_max_health(self, amount: int):
        self.max_health += amount

    def grant_temporary_energy(self, amount: int):
        self.energy += amount

    def increase_strength(self, amount: int):
        self.strength += amount

    def add_card_to_deck(self, card: Card):
        self.deck.append(card)

    def reset_hand(self):
        self.discard_pile.extend(self.hand)
        self.hand.clear()
        for _ in range(self.cards_per_turn):
            self.draw_card()

    def discard_card(self, index: int):
        if 0 <= index < len(self.hand):
            self.discard_pile.append(self.hand.pop(index))

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "health": self.health,
            "max_health": self.max_health,
            "shield": self.shield,
            "bonus_damage": self.bonus_damage,
            "energy": self.energy,
            "max_energy": self.max_energy,
            "symbol": self.symbol,
            "hand_limit": self.hand_limit,
            "deck": [card.to_dict() for card in self.deck],
            "hand": [card.to_dict() for card in self.hand],
            "discard_pile": [card.to_dict() for card in self.discard_pile],
            "size": self.size,
            "shake": self.shake,
            "health_gain_on_skip": self.health_gain_on_skip,
            "cards_drawn_per_turn": self.cards_drawn_per_turn,
            "hp_regain_per_level": self.hp_regain_per_level,
            "status_effects": self.status_effects.to_dict(),
            "relics": [relic.to_dict() for relic in self.relics],
            "strength": self.strength,
            "dodge_chance": self.dodge_chance,
            "cards_per_turn": self.cards_per_turn,
            "phoenix_feather_active": self.phoenix_feather_active,
            "extra_turn_chance": self.extra_turn_chance,
            "applied_permanent_effects": {
                k: list(v) for k, v in self.applied_permanent_effects.items()
            },
            "is_dying": self.is_dying,
            "death_start_time": self.death_start_time,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "Player":
        player = cls(data["name"], data["health"], data["symbol"])
        player.max_health = data["max_health"]
        player.shield = data["shield"]
        player.bonus_damage = data["bonus_damage"]
        player.energy = data["energy"]
        player.max_energy = data["max_energy"]
        player.hand_limit = data["hand_limit"]
        player.deck = [Card.from_dict(card_data) for card_data in data["deck"]]
        player.hand = [Card.from_dict(card_data) for card_data in data["hand"]]
        player.discard_pile = [Card.from_dict(card_data) for card_data in data["discard_pile"]]
        player.size = data["size"]
        player.shake = data["shake"]
        player.health_gain_on_skip = data["health_gain_on_skip"]
        player.cards_drawn_per_turn = data["cards_drawn_per_turn"]
        player.hp_regain_per_level = data["hp_regain_per_level"]
        player.status_effects = StatusEffectManager.from_dict(data["status_effects"])
        player.relics = [Relic.from_dict(relic_data) for relic_data in data["relics"]]
        player.strength = data["strength"]
        player.dodge_chance = data["dodge_chance"]
        player.cards_per_turn = data["cards_per_turn"]
        player.phoenix_feather_active = data["phoenix_feather_active"]
        player.extra_turn_chance = data["extra_turn_chance"]
        player.applied_permanent_effects = {
            k: set(v) for k, v in data["applied_permanent_effects"].items()
        }
        player.is_dying = data["is_dying"]
        player.death_start_time = data["death_start_time"]
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

    def diminish_effects_at_turn_start(self):
        self.status_effects.diminish_effects_at_turn_start()
