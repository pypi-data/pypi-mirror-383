"""ASCII art and visual improvements for the magical roguelike game."""

from typing import Dict, Tuple


class ASCIIChars:
    """Contains all ASCII characters used in the game for better magical visuals."""

    PLAYER = "☿"

    SHADOWLING = "♠"
    WRAITH = "♣"
    ARCANE_GOLEM = "♦"
    CORPSE = "☠"


    HEALING_ELIXIR = "♥"
    ARCANE_ESSENCE = "¤"
    MYSTIC_SCROLL = "♪"
    STAFF = "†"

    FLOOR = "·"
    PORTAL = "⌂"

    WALL_HORIZONTAL = "═"
    WALL_VERTICAL = "║"
    WALL_TOP_LEFT = "╔"
    WALL_TOP_RIGHT = "╗"
    WALL_BOTTOM_LEFT = "╚"
    WALL_BOTTOM_RIGHT = "╝"
    WALL_CROSS = "╬"
    WALL_T_UP = "╩"
    WALL_T_DOWN = "╦"
    WALL_T_LEFT = "╣"
    WALL_T_RIGHT = "╠"

    WALL_EXPLORED = "▓"
    FLOOR_EXPLORED = "░"


class WallRenderer:
    """Handles intelligent wall rendering with proper line characters."""

    def __init__(self, game_map):
        """Initialize the wall renderer.

        Args:
            game_map: 2D array representing the game map
        """
        self.game_map = game_map
        self.height = len(game_map)
        self.width = len(game_map[0]) if game_map else 0

    def get_wall_char(self, x: int, y: int) -> str:
        """Get the appropriate wall character based on surrounding walls.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            Appropriate wall character
        """
        if not self._is_wall(x, y):
            return ASCIIChars.FLOOR

        up = self._is_wall(x, y - 1)
        down = self._is_wall(x, y + 1)
        left = self._is_wall(x - 1, y)
        right = self._is_wall(x + 1, y)

        connections = (up, right, down, left)

        if connections == (True, True, True, True):
            return ASCIIChars.WALL_CROSS
        elif connections == (False, True, True, True):
            return ASCIIChars.WALL_T_DOWN
        elif connections == (True, False, True, True):
            return ASCIIChars.WALL_T_RIGHT
        elif connections == (True, True, False, True):
            return ASCIIChars.WALL_T_UP
        elif connections == (True, True, True, False):
            return ASCIIChars.WALL_T_LEFT
        elif connections == (False, False, True, True):
            return ASCIIChars.WALL_TOP_LEFT
        elif connections == (False, True, True, False):
            return ASCIIChars.WALL_TOP_RIGHT
        elif connections == (True, False, False, True):
            return ASCIIChars.WALL_BOTTOM_LEFT
        elif connections == (True, True, False, False):
            return ASCIIChars.WALL_BOTTOM_RIGHT
        elif connections == (True, False, True, False) or connections == (False, False, False, False):
            return ASCIIChars.WALL_VERTICAL
        elif connections == (False, True, False, True):
            return ASCIIChars.WALL_HORIZONTAL
        else:
            if up or down:
                return ASCIIChars.WALL_VERTICAL
            else:
                return ASCIIChars.WALL_HORIZONTAL

    def _is_wall(self, x: int, y: int) -> bool:
        """Check if a position contains a wall.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            True if position is a wall
        """
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
        return self.game_map[y][x] == '#'


class ColorScheme:
    """Color scheme for different game elements using Textualize rich markup."""

    PLAYER = "[bold bright_magenta]"
    SHADOWLING = "[bright_blue]"
    WRAITH = "[cyan]"
    ARCANE_GOLEM = "[bold bright_cyan]"
    CORPSE = "[dim white]"

    HEALING_ELIXIR = "[bright_green]"
    ARCANE_ESSENCE = "[bright_yellow]"
    MYSTIC_SCROLL = "[bright_blue]"
    STAFF = "[bright_white]"

    WALL = "[bright_white]"
    WALL_EXPLORED = "[dim white]"
    FLOOR = "[dim white]"
    FLOOR_EXPLORED = "[dim black]"
    PORTAL = "[bright_magenta]"

    RESET = "[/]"


def get_colored_char(char: str, color: str) -> str:
    """Get a colored character with Textualize markup.

    Args:
        char: Character to color
        color: Color markup

    Returns:
        Colored character string
    """
    return f"{color}{char}{ColorScheme.RESET}"


def get_entity_display(entity_type: str, is_alive: bool = True) -> str:
    """Get the display character and color for an entity.

    Args:
        entity_type: Type of entity ('player', 'shadowling', 'wraith', 'arcane_golem', 'corpse')
        is_alive: Whether the entity is alive

    Returns:
        Colored character string
    """
    if not is_alive:
        return get_colored_char(ASCIIChars.CORPSE, ColorScheme.CORPSE)

    entity_map = {
        'player': (ASCIIChars.PLAYER, ColorScheme.PLAYER),
        'shadowling': (ASCIIChars.SHADOWLING, ColorScheme.SHADOWLING),
        'wraith': (ASCIIChars.WRAITH, ColorScheme.WRAITH),
        'arcane_golem': (ASCIIChars.ARCANE_GOLEM, ColorScheme.ARCANE_GOLEM),
    }

    if entity_type in entity_map:
        char, color = entity_map[entity_type]
        return get_colored_char(char, color)

    return entity_type

def get_item_display(item_type: str) -> str:
    """Get the display character and color for a magical item.

    Args:
        item_type: Type of magical item

    Returns:
        Colored character string
    """
    item_map = {
        'healing_elixir': (ASCIIChars.HEALING_ELIXIR, ColorScheme.HEALING_ELIXIR),
        'arcane_essence': (ASCIIChars.ARCANE_ESSENCE, ColorScheme.ARCANE_ESSENCE),
        'mystic_scroll': (ASCIIChars.MYSTIC_SCROLL, ColorScheme.MYSTIC_SCROLL),
        'staff': (ASCIIChars.STAFF, ColorScheme.STAFF),
    }

    if item_type in item_map:
        char, color = item_map[item_type]
        return get_colored_char(char, color)

    return item_type
