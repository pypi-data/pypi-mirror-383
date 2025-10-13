"""Combat system for the magical roguelike game."""

import random
from typing import List, Tuple, Optional
from .monster import Monster


class CombatSystem:
    """Handles magical combat mechanics and turn-based gameplay."""

    def __init__(self):
        """Initialize the magical combat system."""
        self.turn_count = 0
        self.combat_log: List[str] = []

    def player_attack_monster(self, player, monster: Monster) -> List[str]:
        """Handle Arcanist casting spells at a magical creature.

        Args:
            player: Player object
            monster: Magical creature to attack

        Returns:
            List of combat messages
        """
        messages = []

        if not monster.is_alive:
            messages.append(f"The {monster.name} has already dissipated!")
            return messages

        base_damage = player.attack_power
        damage = random.randint(max(1, base_damage - 2), base_damage + 3)

        monster_died = monster.take_damage(damage)

        messages.append(f"You cast an arcane bolt at the {monster.name} for {damage} damage!")

        if monster_died:
            messages.append(f"The {monster.name} dissipates into magical energy!")
        else:
            messages.append(f"The {monster.name} has {monster.hp}/{monster.max_hp} HP remaining.")

        return messages

    def monster_attack_player(self, monster: Monster, player) -> List[str]:
        """Handle magical creature attacking Arcanist.

        Args:
            monster: Magical creature attacking
            player: Player object

        Returns:
            List of combat messages
        """
        messages = []

        if not monster.is_alive:
            return messages

        damage = monster.attack(player)
        player.take_damage(damage)

        messages.append(f"The {monster.name} strikes you with dark magic for {damage} damage!")

        if not player.is_alive():
            messages.append("Your magical essence has been extinguished! Game Over!")
        else:
            messages.append(f"You have {player.hp}/{player.max_hp} HP remaining.")

        return messages

    def process_turn(self, player, monster_manager, game_map, visibility_tracker) -> List[str]:
        """Process a complete turn (Arcanist has acted, now creatures act).

        Args:
            player: Player object
            monster_manager: Magical creature manager
            game_map: Game map
            visibility_tracker: FOV tracker

        Returns:
            List of all messages from this turn
        """
        self.turn_count += 1
        all_messages = []

        monster_messages = monster_manager.update_monsters(
            player.x, player.y, game_map, visibility_tracker
        )
        all_messages.extend(monster_messages)

        for monster in monster_manager.monsters:
            if (monster.is_alive and
                monster.is_adjacent_to(player.x, player.y) and
                visibility_tracker.is_visible(monster.x, monster.y)):

                combat_messages = self.monster_attack_player(monster, player)
                all_messages.extend(combat_messages)

        monster_manager.remove_dead_monsters()

        self.combat_log.extend(all_messages)

        if len(self.combat_log) > 10:
            self.combat_log = self.combat_log[-10:]

        return all_messages

    def get_recent_messages(self, count: int = 5) -> List[str]:
        """Get recent magical combat messages.

        Args:
            count: Number of recent messages to return

        Returns:
            List of recent messages
        """
        return self.combat_log[-count:] if self.combat_log else []

    def clear_log(self):
        """Clear the magical combat log."""
        self.combat_log.clear()


class GameState:
    """Manages overall game state and win/lose conditions."""

    def __init__(self):
        """Initialize game state."""
        self.game_over = False
        self.victory = False
        self.current_level = 1
        self.score = 0

    def check_victory_condition(self, player_x: int, player_y: int, game_map) -> bool:
        """Check if Arcanist has reached the arcane portal.

        Args:
            player_x: Arcanist's X coordinate
            player_y: Arcanist's Y coordinate
            game_map: Game map

        Returns:
            True if Arcanist reached portal
        """
        if (0 <= player_x < len(game_map[0]) and
            0 <= player_y < len(game_map) and
            game_map[player_y][player_x] == '⌂'):
            self.victory = True
            return True
        return False

    def check_defeat_condition(self, player) -> bool:
        """Check if Arcanist has been defeated.

        Args:
            player: Player object

        Returns:
            True if Arcanist is defeated
        """
        if not player.is_alive():
            self.game_over = True
            return True
        return False

    def advance_level(self):
        """Advance to the next arcane sanctum."""
        self.current_level += 1
        self.victory = False
        self.score += 100 * self.current_level

    def get_monster_count_for_level(self) -> int:
        """Get the number of magical creatures for current sanctum.

        Returns:
            Number of creatures to spawn
        """
        return min(3 + self.current_level, 10)

    def get_item_count_for_level(self) -> int:
        """Get the number of magical items for current sanctum.

        Returns:
            Number of items to spawn
        """
        return min(5 + self.current_level, 12)

    def add_score(self, points: int):
        """Add points to the arcane score.

        Args:
            points: Points to add
        """
        self.score += points
