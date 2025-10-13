"""Procedural arcane sanctum generation for the magical roguelike."""

import random
from typing import Tuple, List, Set


class DungeonGenerator:
    """Generates procedural arcane sanctums using various algorithms."""

    def __init__(self, width: int, height: int):
        """Initialize the sanctum generator.

        Args:
            width: Width of the sanctum
            height: Height of the sanctum
        """
        self.width = width
        self.height = height

    def generate_random_walk(self, steps: int = 1000) -> List[List[str]]:
        """Generate a sanctum using ethereal walk algorithm.

        Args:
            steps: Number of steps to take in the ethereal walk

        Returns:
            2D list representing the generated sanctum
        """
        sanctum = [['#' for _ in range(self.width)] for _ in range(self.height)]

        x, y = self.width // 2, self.height // 2

        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

        for _ in range(steps):
            if 1 <= x < self.width - 1 and 1 <= y < self.height - 1:
                sanctum[y][x] = '.'

            dx, dy = random.choice(directions)
            new_x, new_y = x + dx, y + dy

            if 1 <= new_x < self.width - 1 and 1 <= new_y < self.height - 1:
                x, y = new_x, new_y

        return sanctum

    def generate_bsp_dungeon(self, min_room_size: int = 6) -> List[List[str]]:
        """Generate a sanctum using Binary Space Partitioning.

        Args:
            min_room_size: Minimum size for ritual chambers

        Returns:
            2D list representing the generated sanctum
        """
        sanctum = [['#' for _ in range(self.width)] for _ in range(self.height)]

        rooms = self._split_space(1, 1, self.width - 2, self.height - 2, min_room_size)

        for room in rooms:
            x, y, w, h = room
            for ry in range(y, y + h):
                for rx in range(x, x + w):
                    if 0 <= rx < self.width and 0 <= ry < self.height:
                        sanctum[ry][rx] = '.'

        self._connect_rooms(sanctum, rooms)

        return sanctum

    def _split_space(self, x: int, y: int, width: int, height: int,
                     min_size: int) -> List[Tuple[int, int, int, int]]:
        """Recursively split space into ritual chambers.

        Args:
            x, y: Top-left corner of the space
            width, height: Dimensions of the space
            min_size: Minimum chamber size

        Returns:
            List of chamber tuples (x, y, width, height)
        """
        rooms = []

        if width < min_size * 2 or height < min_size * 2:
            room_width = max(3, width - 2)
            room_height = max(3, height - 2)
            room_x = x + random.randint(0, max(0, width - room_width))
            room_y = y + random.randint(0, max(0, height - room_height))
            rooms.append((room_x, room_y, room_width, room_height))
            return rooms

        split_horizontal = random.choice([True, False])

        if split_horizontal:
            split_point = random.randint(min_size, height - min_size)
            rooms.extend(self._split_space(x, y, width, split_point, min_size))
            rooms.extend(self._split_space(x, y + split_point, width,
                                         height - split_point, min_size))
        else:
            split_point = random.randint(min_size, width - min_size)
            rooms.extend(self._split_space(x, y, split_point, height, min_size))
            rooms.extend(self._split_space(x + split_point, y,
                                         width - split_point, height, min_size))

        return rooms

    def _connect_rooms(self, sanctum: List[List[str]],
                       rooms: List[Tuple[int, int, int, int]]):
        """Connect ritual chambers with arcane corridors.

        Args:
            sanctum: The sanctum map to modify
            rooms: List of chamber tuples
        """
        for i in range(len(rooms) - 1):
            room1 = rooms[i]
            room2 = rooms[i + 1]

            x1 = room1[0] + room1[2] // 2
            y1 = room1[1] + room1[3] // 2
            x2 = room2[0] + room2[2] // 2
            y2 = room2[1] + room2[3] // 2

            self._carve_corridor(sanctum, x1, y1, x2, y1)
            self._carve_corridor(sanctum, x2, y1, x2, y2)

    def _carve_corridor(self, sanctum: List[List[str]], x1: int, y1: int,
                        x2: int, y2: int):
        """Carve an arcane corridor between two points.

        Args:
            sanctum: The sanctum map to modify
            x1, y1: Start point
            x2, y2: End point
        """
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1

        for x in range(x1, x2 + 1):
            if 0 <= x < self.width and 0 <= y1 < self.height:
                sanctum[y1][x] = '.'

        for y in range(y1, y2 + 1):
            if 0 <= x2 < self.width and 0 <= y < self.height:
                sanctum[y][x2] = '.'

    def find_valid_positions(self, sanctum: List[List[str]],
                           count: int = 2) -> List[Tuple[int, int]]:
        """Find valid ritual positions in the sanctum.

        Args:
            sanctum: The sanctum map
            count: Number of positions to find

        Returns:
            List of (x, y) tuples for valid positions
        """
        floor_tiles = []
        for y in range(len(sanctum)):
            for x in range(len(sanctum[0])):
                if sanctum[y][x] == '.':
                    floor_tiles.append((x, y))

        if len(floor_tiles) < count:
            return floor_tiles

        return random.sample(floor_tiles, count)
