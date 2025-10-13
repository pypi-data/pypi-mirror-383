"""Item and inventory system for the magical roguelike game."""

import random
from typing import List, Dict, Optional, Tuple
from enum import Enum


class ItemType(Enum):
    """Different types of magical items."""
    HEALING_ELIXIR = ("♥", "Healing Elixir", "Restores 25 HP with arcane energy")
    ARCANE_ESSENCE = ("¤", "Arcane Essence", "Pure magical energy used as currency")
    MYSTIC_SCROLL = ("♪", "Mystic Scroll", "Ancient scroll with unpredictable magical effects")
    STAFF = ("†", "Elderwood Staff", "Focuses magical power, increasing spell potency")


class Item:
    """Represents a magical item in the game."""

    def __init__(self, x: int, y: int, item_type: ItemType, value: int = 1):
        """Initialize a magical item.

        Args:
            x: X coordinate
            y: Y coordinate
            item_type: Type of magical item
            value: Value/quantity of the item
        """
        self.x = x
        self.y = y
        self.item_type = item_type
        self.symbol = item_type.value[0]
        self.name = item_type.value[1]
        self.description = item_type.value[2]
        self.value = value
        self.is_collected = False

    def use(self, player) -> str:
        """Use the magical item on the Arcanist.

        Args:
            player: Player object

        Returns:
            Message describing the magical effect
        """
        if self.item_type == ItemType.HEALING_ELIXIR:
            heal_amount = min(25, player.max_hp - player.hp)
            player.hp += heal_amount
            return f"You drink the healing elixir and recover {heal_amount} HP through arcane restoration!"

        elif self.item_type == ItemType.MYSTIC_SCROLL:
            effect = random.choice([
                "heal", "empower", "nothing"
            ])

            if effect == "heal":
                heal_amount = random.randint(10, 30)
                player.hp = min(player.max_hp, player.hp + heal_amount)
                return f"The scroll glows with healing energy, restoring {heal_amount} HP!"
            elif effect == "empower":
                player.attack_power += 2
                return "The scroll channels ancient power into you! Spell potency +2!"
            else:
                return "The scroll crumbles to arcane dust. The magic fizzles out."

        elif self.item_type == ItemType.STAFF:
            player.attack_power += 5
            return "You attune to the Elderwood Staff! Your spell power increases by 5!"

        elif self.item_type == ItemType.ARCANE_ESSENCE:
            return f"You collect {self.value} units of arcane essence!"

        return f"You can't use the {self.name} in this way."


class Inventory:
    """Manages the Arcanist's arcane inventory."""

    def __init__(self):
        """Initialize an empty arcane inventory."""
        self.items: Dict[ItemType, int] = {}
        self.essence = 0

    def add_item(self, item: Item) -> str:
        """Add a magical item to the inventory.

        Args:
            item: Magical item to add

        Returns:
            Message describing what was added
        """
        if item.item_type == ItemType.ARCANE_ESSENCE:
            self.essence += item.value
            return f"Collected {item.value} arcane essence!"
        else:
            if item.item_type in self.items:
                self.items[item.item_type] += item.value
            else:
                self.items[item.item_type] = item.value
            return f"Acquired {item.name}!"

    def use_item(self, item_type: ItemType, player) -> Optional[str]:
        """Use a magical item from the inventory.

        Args:
            item_type: Type of magical item to use
            player: Player object

        Returns:
            Message describing the magical effect, or None if item not available
        """
        if item_type not in self.items or self.items[item_type] <= 0:
            return None

        temp_item = Item(0, 0, item_type)
        effect_message = temp_item.use(player)

        self.items[item_type] -= 1
        if self.items[item_type] <= 0:
            del self.items[item_type]

        return effect_message

    def get_item_count(self, item_type: ItemType) -> int:
        """Get the count of a specific magical item type.

        Args:
            item_type: Type of magical item

        Returns:
            Number of items of that type
        """
        return self.items.get(item_type, 0)

    def get_inventory_display(self) -> str:
        """Get a string representation of the arcane inventory.

        Returns:
            Formatted inventory string
        """
        lines = [f"Arcane Essence: {self.essence}"]

        for item_type, count in self.items.items():
            lines.append(f"{item_type.value[1]}: {count}")

        return "\n".join(lines) if lines else "Arcane inventory empty"


class ItemManager:
    """Manages all magical items in the game world."""

    def __init__(self):
        """Initialize the magical item manager."""
        self.items: List[Item] = []

    def spawn_items(self, game_map, count: int = 8):
        """Spawn magical items randomly on the map.

        Args:
            game_map: Game map to spawn items on
            count: Number of magical items to spawn
        """
        from .dungeon_generator import DungeonGenerator

        generator = DungeonGenerator(len(game_map[0]), len(game_map))
        positions = generator.find_valid_positions(game_map, count)

        for i, (x, y) in enumerate(positions):

            rand = random.random()

            if rand < 0.4:
                item_type = ItemType.ARCANE_ESSENCE
                value = random.randint(5, 20)
            elif rand < 0.7:
                item_type = ItemType.HEALING_ELIXIR
                value = 1
            elif rand < 0.9:
                item_type = ItemType.MYSTIC_SCROLL
                value = 1
            else:
                item_type = ItemType.STAFF
                value = 1

            item = Item(x, y, item_type, value)
            self.items.append(item)

    def get_item_at(self, x: int, y: int) -> Optional[Item]:
        """Get magical item at specific position.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Magical item at position or None
        """
        for item in self.items:
            if item.x == x and item.y == y and not item.is_collected:
                return item
        return None

    def collect_item(self, x: int, y: int) -> Optional[Item]:
        """Collect a magical item at the specified position.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Collected magical item or None
        """
        item = self.get_item_at(x, y)
        if item:
            item.is_collected = True
            return item
        return None

    def get_visible_items(self, visibility_tracker) -> List[Item]:
        """Get all magical items that are currently visible.

        Args:
            visibility_tracker: FOV tracker

        Returns:
            List of visible magical items
        """
        visible_items = []
        for item in self.items:
            if (not item.is_collected and
                visibility_tracker.is_visible(item.x, item.y)):
                visible_items.append(item)
        return visible_items
