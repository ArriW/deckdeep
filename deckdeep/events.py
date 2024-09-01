import random
from deckdeep.card import Card
from deckdeep.relic import get_relic_by_name, Relic
from deckdeep.player import Player
from deckdeep.render import handle_card_selection
from deckdeep.logger import GameLogger


class Event:
    def __init__(self, name: str, description: str, options: list):
        self.name = name
        self.description = description
        self.options = options

    def execute_option(self, option_method, player, assets):
        method = getattr(self, option_method)
        if "assets" in method.__code__.co_varnames:
            return method(player, assets)
        else:
            return method(player)


class VoodooDoctor(Event):
    def __init__(self):
        healing_charm = get_relic_by_name("Healing Charm")
        super().__init__(
            "Voodoo Doctor",
            f"A mysterious figure offers you various magical remedies. You can pay 10 HP and gain a curse to be granted a '{healing_charm.name}' relic, or accept a sketchy potion with unknown effects.",
            [
                ("Get Healing Charm", "healing_charm"),
                ("Take sketchy potion", "sketchy_potion"),
                ("Leave", "leave"),
            ],
        )

    def healing_charm(self, player):
        if player.health > 10:
            player.health -= 10
            curse = Card("Cursed Coin", 99, 0.1, health_cost=5)
            player.deck.append(curse)
            healing_charm = get_relic_by_name("Healing Charm")
            player.relics.append(healing_charm)
            return f"You gained the '{healing_charm.name}' relic. {healing_charm.description}"
        return "You don't have enough HP to pay for the Healing Charm."

    def sketchy_potion(self, player: Player):
        possible_outcomes = [
            lambda: setattr(player, "energy", player.energy + 10),
            lambda: setattr(player, "health", player.health + 10),
            lambda: setattr(player, "max_health", player.max_health + 10),
            lambda: setattr(player, "shield", player.shield + 10),
        ]
        select_random_outcome = random.choice(possible_outcomes)
        select_random_outcome()
        return f"You gained a random benefit from the potion. That benefit was {select_random_outcome.__name__}."

    def leave(self, player):
        return "You leave the Voodoo Doctor's tent."


class Medic(Event):
    def __init__(self):
        hair_of_dog = get_relic_by_name("Hair of the Dog")
        super().__init__(
            "Medic",
            f"You find a medic tent. You can pay 20 HP to gain a {hair_of_dog.name} or heal 50 HP.",
            [
                ("Get Hair of the Dog", "grant_hair_of_the_dog"),
                ("Heal 50 HP", "heal"),
                ("Leave", "leave"),
            ],
        )

    def grant_hair_of_the_dog(self, player):
        if player.health > 20:
            player.health -= 20
            relic = get_relic_by_name("Hair of the Dog")
            player.relics.append(relic)
            relic.apply_effect(player, None)
            return f"You gained the '{relic.name}' relic. {relic.description}"
        return "You don't have enough HP to pay for the Vitality Boost."

    def heal(self, player):
        player.heal(h := 50)
        return f"You healed {h} HP."

    def leave(self, player):
        return "You leave the Medic's tent."


class Priest(Event):
    def __init__(self):
        super().__init__(
            "Priest",
            "A holy figure offers spiritual assistance. You can heal for 50 HP or cleanse one of your misdeeds.",
            [
                ("Heal 50 HP", "heal"),
                ("Remove a curse", "remove_curse"),
                ("Leave", "leave"),
            ],
        )

    def heal(self, player):
        player.heal(h := 50)
        return f"You healed for {h} HP."

    def remove_curse(self, player):
        player.remove_curses(1)
        return "You removed a curse from your deck."

    def leave(self, player):
        return "You leave the Priest's temple."


class Thrifter(Event):
    def __init__(self):
        super().__init__(
            "Thrifter",
            "A merchant offers to remove a card from your deck for a price of 25% of your current HP.",
            [
                ("Remove a card", "remove_card"),
                ("Leave", "leave"),
            ],
        )

    def remove_card(self, player, assets):
        cost = int(player.health * 0.25)
        if player.health > cost:
            player.health -= cost
            full_deck = player.get_sorted_full_deck()
            chosen_index = handle_card_selection(full_deck, assets, player)
            if chosen_index is not None:
                removed_card = player.remove_card_from_deck(chosen_index)
                if removed_card:
                    return f"You paid {cost} HP to remove {removed_card.name} from your deck."
                else:
                    return "Invalid card index. No card was removed."
            return "No card was selected."
        return "You don't have enough HP to remove a card."

    def leave(self, player, assets):
        return "You leave the Thrifter's shop."


class CursedWell(Event):
    def __init__(self):
        cursed_coin = get_relic_by_name("Cursed Coin")
        super().__init__(
            "Cursed Well",
            f"A mysterious well emanates dark energy. You can add a curse to your deck and gain a '{cursed_coin.name}' relic.",
            [
                ("Embrace dark power", "dark_power"),
                ("Leave", "leave"),
            ],
        )

    def dark_power(self, player):
        curse = Card("Cursed Coin", 99, 0.1, health_cost=5)
        player.deck.append(curse)
        relic = get_relic_by_name("Cursed Coin")
        player.relics.append(relic)
        return f"You gained the '{relic.name}' relic ({relic.description}) and added a curse to your deck."

    def leave(self, player):
        return "You back away from the Cursed Well."


class Scribe(Event):
    def __init__(self):
        super().__init__(
            "Scribe",
            "In a dimly lit study, you encounter a wizened scribe surrounded by ancient tomes and scrolls. "
            "The air crackles with magical energy as the scribe offers to duplicate one of your cards.",
            [
                (
                    "Duplicate a card (Add 1 copy of a card to your deck)",
                    "duplicate_card",
                ),
                ("Leave", "leave"),
            ],
        )

    def duplicate_card(self, player, assets):
        full_deck = player.get_sorted_full_deck()
        chosen_index = handle_card_selection(full_deck, assets, player)
        if chosen_index is not None:
            duplicated_card = player.duplicate_card_in_deck(chosen_index)
            if duplicated_card:
                return (
                    f"The scribe's quill dances across a blank parchment, creating an exact copy of your '{duplicated_card.name}'. "
                    f"A duplicate has been added to your deck."
                )
            else:
                return "The scribe frowns. Something went wrong, and no card was duplicated."
        return "You decide not to duplicate any card."

    def leave(self, player, assets):
        return (
            "You thank the scribe for their offer but decide to continue on your journey. "
            "The scribe nods understanding, returning to their arcane studies."
        )


class AncientLibrary(Event):
    def __init__(self):
        paper_weight = get_relic_by_name("Paper Weight")
        super().__init__(
            "Ancient Library",
            f"A vast library of ancient knowledge stands before you. You can offer a quarter of your health and 1 max energy to gain a '{paper_weight.name}' - {paper_weight.description}",
            [
                ("Gain knowledge", "paper_weight"),
                ("Leave", "leave"),
            ],
        )

    def paper_weight(self, player):
        player.relics.append(get_relic_by_name("Paper Weight"))
        return "You gained the Paper Weight relic."

    def leave(self, player):
        return "You leave the Ancient Library."


class ForgottenShrine(Event):
    def __init__(self):
        relic = get_relic_by_name("Energy Crystal")
        super().__init__(
            "Forgotten Shrine",
            f"A shrine stands before you, covered in moss and vines. It seems to be calling out to you. You can offer half of your max health to gain the '{relic.name}' relic or cleanse the shrine to remove all curses from your deck.",
            [
                ("Offer health", "energy_crystal"),
                ("Cleanse shrine", "cleanse"),
                ("Leave", "leave"),
            ],
        )

    def energy_crystal(self, player):
        cost = player.max_health // 2
        if player.health > cost:
            player.health -= cost
            energy_crystal = get_relic_by_name("Energy Crystal")
            player.relics.append(energy_crystal)
            return f"You gained the '{energy_crystal.name}' relic. {energy_crystal.description}"
        return "You don't have enough HP to make the offering."

    def cleanse(self, player: Player):
        player.remove_curses(-1)
        return "All curses have been removed from your deck."

    def leave(self, player):
        return "You leave the Forgotten Shrine undisturbed."


class RestSite(Event):
    def __init__(self):
        self.heal_amount = 50
        self.energy_gain = 2
        self.damage_gain = 2

        super().__init__(
            "Rest Site",
            "You discover a tranquil clearing in the forest. A mystical fountain bubbles nearby, and an ancient altar stands silent. The air is thick with restorative energy.",
            [
                (f"Drink from the fountain (Heal {self.heal_amount} HP)", "heal"),
                (
                    f"Meditate at the altar (Gain {self.energy_gain} energy and {self.damage_gain} bonus damage)",
                    "boost",
                ),
                (
                    "Offer a card to the forest spirits (Remove 1 card from your deck)",
                    "remove_card",
                ),
                ("Continue your journey", "leave"),
            ],
        )

    def heal(self, player, assets):
        player.heal(self.heal_amount)
        return f"You drink from the fountain. Its cool, sparkling water restores {self.heal_amount} HP."

    def boost(self, player, assets):
        player.energy += self.energy_gain
        player.bonus_damage += self.damage_gain
        return f"You meditate at the altar. Ancient wisdom flows through you, granting {self.energy_gain} energy and {self.damage_gain} bonus damage."

    def remove_card(self, player, assets):
        full_deck = player.get_sorted_full_deck()
        chosen_index = handle_card_selection(full_deck, assets)
        if chosen_index is not None:
            removed_card = player.remove_card_from_deck(chosen_index)
            if removed_card:
                return f"You offer {removed_card.name} to the forest spirits. It dissolves into motes of light, forever leaving your deck."
            else:
                return "The spirits reject your offering. No card was removed."
        return "You decide not to make an offering."

    def leave(self, player, assets):
        return "You leave the peaceful clearing, feeling refreshed and ready to face new challenges."


class Defender(Event):
    def __init__(self):
        self.damage_percentage = 20
        self.shield_rune = get_relic_by_name("Shield Rune")

        super().__init__(
            "Defender",
            f"A caravan of travelers has been ambushed by bandits. Defend and help them, suffering {self.damage_percentage}% of your current health as damage, and be rewarded the '{self.shield_rune.name}'.",
            [
                (
                    f"Defend caravan (Take {self.damage_percentage}% damage, gain '{self.shield_rune.name}')",
                    "defend",
                ),
                ("Leave (Abandon a card from your deck)", "leave"),
            ],
        )

    def defend(self, player, assets):
        damage = int(player.health * (self.damage_percentage / 100))
        player.health -= damage
        player.relics.append(self.shield_rune)
        return f"You bravely defended the caravan, taking {damage} damage. You gained the '{self.shield_rune.name}' relic. {self.shield_rune.description}"

    def leave(self, player, assets):
        full_deck = player.get_sorted_full_deck()
        chosen_index = handle_card_selection(full_deck, assets)
        if chosen_index is not None:
            removed_card = player.remove_card_from_deck(chosen_index)
            if removed_card:
                return f"You hastily flee the scene, abandoning your '{removed_card.name}' in the process. It's lost forever from your deck."
            else:
                return "Something went wrong. No card was removed."
        return "You must abandon a card to leave. The event continues."


class DarkMerchant(Event):
    def __init__(self):
        cursed_dagger = get_relic_by_name("Cursed Dagger")
        super().__init__(
            "Dark Merchant",
            f"A shadowy figure appears offers you a mysterious dagger. A Do you can accept the '{cursed_dagger.name}' in exchange for 15 max HP?",
            [
                ("Accept dagger", "accept_dagger"),
                ("Decline and leave", "leave"),
            ],
        )

    def accept_dagger(self, player):
        if player.max_health > 15:
            player.max_health -= 15
            player.health = min(player.health, player.max_health)
            cursed_dagger = get_relic_by_name("Cursed Dagger")
            player.relics.append(cursed_dagger)
            return f"You accepted the '{cursed_dagger.name}'. Your max HP decreased by 15, but you gained a powerful relic. {cursed_dagger.description}"
        return "You don't have enough max HP to make the exchange."

    def leave(self, player):
        return "You decline the mysterious offer and walk away."


def get_random_event():
    events = [
        Medic(),
        VoodooDoctor(),
        Thrifter(),
        CursedWell(),
        Scribe(),
        ForgottenShrine(),
        RestSite(),
        Defender(),
        DarkMerchant(),
        Priest(),
        AncientLibrary(),
    ]
    return random.choice(events)
