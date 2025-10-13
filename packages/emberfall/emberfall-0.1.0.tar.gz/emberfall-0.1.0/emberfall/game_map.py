"""Game map system for the magical roguelike."""

from typing import List, Tuple, Optional
from .dungeon_generator import DungeonGenerator
from .fov import FOVCalculator, VisibilityTracker
from .ascii_art import WallRenderer, ASCIIChars, ColorScheme, get_colored_char


class GameMap:
    """Represents the arcane sanctum map and handles map-related operations."""

    def __init__(self, width: int = 80, height: int = 40, use_procedural: bool = True):
        """Initialize an arcane sanctum map.

        Args:
            width: Width of the sanctum
            height: Height of the sanctum
            use_procedural: Whether to use procedural generation
        """
        self.width = width
        self.height = height
        self.use_procedural = use_procedural

        if use_procedural:
            self.tiles = self._generate_procedural_map()
        else:
            self.tiles = self._create_simple_map()

        self.fov_calculator = FOVCalculator(self.tiles)
        self.visibility_tracker = VisibilityTracker()

        self.wall_renderer = WallRenderer(self.tiles)

        self.player_start, self.exit_pos = self._find_special_positions()

    def _generate_procedural_map(self) -> List[List[str]]:
        """Generate a procedural arcane sanctum.

        Returns:
            2D list representing the sanctum
        """
        generator = DungeonGenerator(self.width, self.height)

        return generator.generate_bsp_dungeon()

    def _create_simple_map(self) -> List[List[str]]:
        """Create a simple hardcoded sanctum for testing.

        Returns:
            2D list representing the sanctum
        """
        map_data = []

        for y in range(self.height):
            row = []
            for x in range(self.width):
                if (x == 0 or x == self.width - 1 or
                    y == 0 or y == self.height - 1):
                    row.append('#')
                else:
                    row.append('.')
            map_data.append(row)

        for y in range(5, 15):
            if y < len(map_data) and 10 < len(map_data[y]):
                map_data[y][10] = '#'

        for x in range(15, 25):
            if 10 < len(map_data) and x < len(map_data[10]):
                map_data[10][x] = '#'

        return map_data

    def _find_special_positions(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Find positions for Arcanist start and arcane portal.

        Returns:
            Tuple of (arcanist_start, portal_position)
        """
        generator = DungeonGenerator(self.width, self.height)
        positions = generator.find_valid_positions(self.tiles, 2)

        if len(positions) >= 2:
            return positions[0], positions[1]
        elif len(positions) == 1:
            return positions[0], positions[0]
        else:
            return (self.width // 2, self.height // 2), (self.width // 2 + 1, self.height // 2)

    def place_exit(self):
        """Place the arcane portal on the map."""
        if self.exit_pos:
            x, y = self.exit_pos
            if 0 <= x < self.width and 0 <= y < self.height:
                self.tiles[y][x] = '⌂'

    def get_tile(self, x: int, y: int) -> str:
        """Get the tile at given coordinates.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Character representing the tile
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[y][x]
        return '#'

    def is_walkable(self, x: int, y: int) -> bool:
        """Check if a tile is walkable.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if the tile can be walked on
        """
        tile = self.get_tile(x, y)
        return tile in ['.', '⌂']

    def update_fov(self, player_x: int, player_y: int):
        """Update the arcane sight from Arcanist position.

        Args:
            player_x: Arcanist's X coordinate
            player_y: Arcanist's Y coordinate
        """
        visible_tiles = self.fov_calculator.calculate_simple_fov(player_x, player_y)
        self.visibility_tracker.update_visibility(visible_tiles)

    def render_with_entities(self, player_x: int, player_y: int,
                           monster_manager=None, item_manager=None) -> str:
        """Render the sanctum with the Arcanist position, arcane sight, creatures, and magical items.

        Args:
            player_x: Arcanist's X coordinate
            player_y: Arcanist's Y coordinate
            monster_manager: Magical creature manager for rendering creatures
            item_manager: Magical item manager for rendering items

        Returns:
            String representation of the sanctum
        """
        lines = []
        for y in range(self.height):
            line = ""
            for x in range(self.width):
                if x == player_x and y == player_y:
                    line += get_colored_char('☿', ColorScheme.PLAYER)
                elif (monster_manager and
                      self.visibility_tracker.is_visible(x, y)):
                    monster = monster_manager.get_monster_at(x, y)
                    if monster:
                        if monster.is_alive:
                            if monster.monster_type.name == 'SHADOWLING':
                                line += get_colored_char(monster.symbol, ColorScheme.SHADOWLING)
                            elif monster.monster_type.name == 'WRAITH':
                                line += get_colored_char(monster.symbol, ColorScheme.WRAITH)
                            elif monster.monster_type.name == 'ARCANE_GOLEM':
                                line += get_colored_char(monster.symbol, ColorScheme.ARCANE_GOLEM)
                            else:
                                line += monster.symbol
                        else:
                            line += get_colored_char(monster.symbol, ColorScheme.CORPSE)
                    elif (item_manager):
                        item = item_manager.get_item_at(x, y)
                        if item:
                            if item.item_type.name == 'HEALING_ELIXIR':
                                line += get_colored_char(item.symbol, ColorScheme.HEALING_ELIXIR)
                            elif item.item_type.name == 'ARCANE_ESSENCE':
                                line += get_colored_char(item.symbol, ColorScheme.ARCANE_ESSENCE)
                            elif item.item_type.name == 'MYSTIC_SCROLL':
                                line += get_colored_char(item.symbol, ColorScheme.MYSTIC_SCROLL)
                            elif item.item_type.name == 'STAFF':
                                line += get_colored_char(item.symbol, ColorScheme.STAFF)
                            else:
                                line += item.symbol
                        else:
                            if self.tiles[y][x] == '⌂':
                                line += get_colored_char('⌂', ColorScheme.PORTAL)
                            else:
                                line += get_colored_char('·', ColorScheme.FLOOR)
                    else:
                        if self.tiles[y][x] == '⌂':
                            line += get_colored_char('⌂', ColorScheme.PORTAL)
                        else:
                            line += get_colored_char('·', ColorScheme.FLOOR)
                elif self.visibility_tracker.is_visible(x, y):
                    if item_manager:
                        item = item_manager.get_item_at(x, y)
                        if item:
                            if item.item_type.name == 'HEALING_ELIXIR':
                                line += get_colored_char(item.symbol, ColorScheme.HEALING_ELIXIR)
                            elif item.item_type.name == 'ARCANE_ESSENCE':
                                line += get_colored_char(item.symbol, ColorScheme.ARCANE_ESSENCE)
                            elif item.item_type.name == 'MYSTIC_SCROLL':
                                line += get_colored_char(item.symbol, ColorScheme.MYSTIC_SCROLL)
                            elif item.item_type.name == 'STAFF':
                                line += get_colored_char(item.symbol, ColorScheme.STAFF)
                            else:
                                line += item.symbol
                        else:
                            if self.tiles[y][x] == '⌂':
                                line += get_colored_char('⌂', ColorScheme.PORTAL)
                            else:
                                line += get_colored_char('·', ColorScheme.FLOOR)
                    else:
                        if self.tiles[y][x] == '⌂':
                            line += get_colored_char('⌂', ColorScheme.PORTAL)
                        else:
                            line += get_colored_char('·', ColorScheme.FLOOR)
                elif self.visibility_tracker.is_explored(x, y) or self.tiles[y][x] == '#':
                    tile = self.tiles[y][x]
                    if tile == '#':
                        wall_char = self.wall_renderer.get_wall_char(x, y)
                        if self.visibility_tracker.is_explored(x, y):
                            line += get_colored_char(wall_char, ColorScheme.WALL)
                        else:
                            line += get_colored_char(wall_char, ColorScheme.WALL_EXPLORED)
                    else:
                        line += get_colored_char('░', ColorScheme.FLOOR_EXPLORED)
                else:
                    line += ' '
            lines.append(line)
        return '\n'.join(lines)
