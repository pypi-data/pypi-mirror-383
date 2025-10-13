"""Monster system for the magical roguelike game."""

import random
from typing import List, Tuple, Optional
from enum import Enum


class MonsterType(Enum):
    """Different types of arcane creatures."""
    SHADOWLING = ("♠", 20, 5, "Shadowling")
    WRAITH = ("♣", 35, 8, "Wraith")
    ARCANE_GOLEM = ("♦", 100, 15, "Arcane Golem")


class Monster:
    """Represents a magical creature in the game."""

    def __init__(self, x: int, y: int, monster_type: MonsterType):
        """Initialize a magical creature.

        Args:
            x: X coordinate
            y: Y coordinate
            monster_type: Type of magical creature
        """
        self.x = x
        self.y = y
        self.monster_type = monster_type
        self.symbol = monster_type.value[0]
        self.max_hp = monster_type.value[1]
        self.hp = self.max_hp
        self.attack_power = monster_type.value[2]
        self.name = monster_type.value[3]
        self.is_alive = True

    def take_damage(self, damage: int) -> bool:
        """Apply arcane damage to the creature.

        Args:
            damage: Amount of damage to take

        Returns:
            True if creature dissipated from this damage
        """
        self.hp = max(0, self.hp - damage)
        if self.hp <= 0:
            self.is_alive = False
            self.symbol = '☠'
            return True
        return False

    def attack(self, target) -> int:
        """Attack a target with magical energy.

        Args:
            target: Target to attack (usually player)

        Returns:
            Arcane damage dealt
        """
        if not self.is_alive:
            return 0

        damage = random.randint(max(1, self.attack_power - 2), self.attack_power + 2)
        return damage

    def move_towards(self, target_x: int, target_y: int, game_map) -> bool:
        """Move one step towards target position.

        Args:
            target_x: Target X coordinate
            target_y: Target Y coordinate
            game_map: Game map for collision detection

        Returns:
            True if moved successfully
        """
        if not self.is_alive:
            return False

        dx = 0
        dy = 0

        if target_x > self.x:
            dx = 1
        elif target_x < self.x:
            dx = -1

        if target_y > self.y:
            dy = 1
        elif target_y < self.y:
            dy = -1

        new_x = self.x + dx
        new_y = self.y + dy

        if (0 <= new_x < len(game_map[0]) and
            0 <= new_y < len(game_map) and
            game_map[new_y][new_x] != '#'):
            self.x = new_x
            self.y = new_y
            return True

        return False

    def distance_to(self, x: int, y: int) -> float:
        """Calculate distance to a point.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Distance to the point
        """
        return ((self.x - x) ** 2 + (self.y - y) ** 2) ** 0.5

    def is_adjacent_to(self, x: int, y: int) -> bool:
        """Check if creature is adjacent to a position.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if adjacent
        """
        return abs(self.x - x) <= 1 and abs(self.y - y) <= 1 and (self.x != x or self.y != y)


class MonsterManager:
    """Manages all magical creatures in the game."""

    def __init__(self):
        """Initialize the creature manager."""
        self.monsters: List[Monster] = []

    def spawn_monsters(self, game_map, count: int = 5, level: int = 1):
        """Spawn magical creatures on the map.

        Args:
            game_map: Game map to spawn creatures on
            count: Number of creatures to spawn
            level: Current arcane sanctum level for difficulty scaling
        """
        from .dungeon_generator import DungeonGenerator

        generator = DungeonGenerator(len(game_map[0]), len(game_map))
        positions = generator.find_valid_positions(game_map, count)

        for i, (x, y) in enumerate(positions):
            rand = random.random()

            if level == 1:
                if rand < 0.8:
                    monster_type = MonsterType.SHADOWLING
                else:
                    monster_type = MonsterType.WRAITH
            elif level <= 3:
                if rand < 0.5:
                    monster_type = MonsterType.SHADOWLING
                elif rand < 0.9:
                    monster_type = MonsterType.WRAITH
                else:
                    monster_type = MonsterType.ARCANE_GOLEM
            else:
                if rand < 0.3:
                    monster_type = MonsterType.SHADOWLING
                elif rand < 0.7:
                    monster_type = MonsterType.WRAITH
                else:
                    monster_type = MonsterType.ARCANE_GOLEM

            monster = Monster(x, y, monster_type)

            if level > 1:
                bonus_hp = (level - 1) * 5
                bonus_attack = (level - 1) * 2
                monster.max_hp += bonus_hp
                monster.hp += bonus_hp
                monster.attack_power += bonus_attack

            self.monsters.append(monster)

    def get_monster_at(self, x: int, y: int) -> Optional[Monster]:
        """Get creature at specific position.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Creature at position or None
        """
        for monster in self.monsters:
            if monster.x == x and monster.y == y and monster.is_alive:
                return monster
        return None

    def remove_dead_monsters(self):
        """Remove dissipated creatures from the list."""
        self.monsters = [m for m in self.monsters if m.is_alive]

    def update_monsters(self, player_x: int, player_y: int, game_map,
                       visibility_tracker) -> List[str]:
        """Update all creatures (AI and movement).

        Args:
            player_x: Arcanist's X coordinate
            player_y: Arcanist's Y coordinate
            game_map: Game map
            visibility_tracker: FOV tracker

        Returns:
            List of action messages
        """
        messages = []

        for monster in self.monsters[:]:
            if not monster.is_alive:
                continue

            if not visibility_tracker.is_visible(monster.x, monster.y):
                continue

            if monster.is_adjacent_to(player_x, player_y):
                damage = monster.attack(None)
                messages.append(f"{monster.name} strikes with arcane energy for {damage} damage!")
            else:
                distance = monster.distance_to(player_x, player_y)
                if distance <= 8:
                    if self._can_see_player(monster, player_x, player_y, game_map):
                        old_x, old_y = monster.x, monster.y
                        if monster.move_towards(player_x, player_y, game_map):
                            conflicting_monster = self.get_monster_at(monster.x, monster.y)
                            if conflicting_monster and conflicting_monster != monster:
                                monster.x, monster.y = old_x, old_y

        return messages

    def _can_see_player(self, monster: Monster, player_x: int, player_y: int,
                       game_map) -> bool:
        """Check if creature can sense the Arcanist.

        Args:
            monster: The magical creature
            player_x: Arcanist's X coordinate
            player_y: Arcanist's Y coordinate
            game_map: Game map

        Returns:
            True if creature can sense Arcanist
        """
        dx = abs(player_x - monster.x)
        dy = abs(player_y - monster.y)

        if dx == 0 and dy == 0:
            return True

        x1, y1 = monster.x, monster.y
        x2, y2 = player_x, player_y

        x_step = 1 if x1 < x2 else -1
        y_step = 1 if y1 < y2 else -1

        if dx > dy:
            error = dx / 2
            y = y1
            for x in range(x1, x2, x_step):
                if game_map[y][x] == '#':
                    return False
                error -= dy
                if error < 0:
                    y += y_step
                    error += dx
        else:
            error = dy / 2
            x = x1
            for y in range(y1, y2, y_step):
                if game_map[y][x] == '#':
                    return False
                error -= dx
                if error < 0:
                    x += x_step
                    error += dy

        return True
