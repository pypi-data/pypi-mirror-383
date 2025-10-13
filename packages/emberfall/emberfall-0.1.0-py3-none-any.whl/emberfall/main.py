"""Main game file for the magical roguelike using Textualize."""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Header, Footer
from textual.binding import Binding

from .player import Player
from .game_map import GameMap
from .monster import MonsterManager
from .combat import CombatSystem, GameState
from .items import ItemManager, ItemType
from .fov import FOVCalculator, VisibilityTracker



class GameDisplay(Static):
    """Widget to display the arcane sanctum and Arcanist."""

    def __init__(self, game_map: GameMap, player: Player, monster_manager: MonsterManager,
                 item_manager: ItemManager, game_state: GameState):
        super().__init__()
        self.game_map = game_map
        self.player = player
        self.monster_manager = monster_manager
        self.item_manager = item_manager
        self.game_state = game_state
        self.update_display()

    def update_display(self):
        """Update the display with current game state."""
        if self.game_state and self.game_state.game_over:
            game_over_text = """
[bold red on black]
╔══════════════════════════════════════╗
║                                      ║
║         ARCANE ESSENCE EXTINGUISHED  ║
║              GAME OVER               ║
║                                      ║
║         Press 'r' to restart         ║
║         Press 'q' to quit            ║
║                                      ║
╚══════════════════════════════════════╝
[/]
"""
            self.update(game_over_text)
        else:
            map_str = self.game_map.render_with_entities(
                self.player.x, self.player.y, self.monster_manager, self.item_manager
            )
            self.update(f"[white on black]{map_str}[/]")


class StatusDisplay(Static):
    """Widget to display Arcanist status information."""

    def __init__(self, player: Player, game_state: GameState):
        super().__init__()
        self.player = player
        self.game_state = game_state
        self.update_status()

    def update_status(self):
        """Update the status display."""
        inventory_str = self.player.inventory.get_inventory_display()
        status_text = f"""
[bold]Arcanist Status[/bold]
HP: {self.player.hp}/{self.player.max_hp}
Position: ({self.player.x}, {self.player.y})
Spell Power: {self.player.attack_power}
Sanctum Level: {self.game_state.current_level}
Arcane Score: {self.game_state.score}

[bold]Arcane Inventory[/bold]
{inventory_str}
        """
        self.update(status_text.strip())


class MessageDisplay(Static):
    """Widget to display magical game messages."""

    def __init__(self, combat_system: CombatSystem):
        super().__init__()
        self.combat_system = combat_system
        self.update_messages()

    def update_messages(self):
        """Update the message display."""
        messages = self.combat_system.get_recent_messages(5)
        if messages:
            message_text = "\n".join(messages)
        else:
            message_text = "Welcome to the Arcane Sanctum!\nUse WASD or arrows to move.\nCast spells at creatures (♠♣♦) by moving into them.\nCollect magical items (♥¤♪†) and press 1/2 to use them."

        self.update(f"[bold]Arcane Chronicles[/bold]\n{message_text}")


class RoguelikeApp(App):
    """Main application class for the magical roguelike game."""

    CSS = """
    Screen {
        layout: horizontal;
    }

    #game_area {
        width: 4fr;
        border: solid white;
        padding: 1;
        overflow: auto;
    }

    #info_area {
        width: 1fr;
        layout: vertical;
        margin-left: 1;
        min-width: 30;
    }

    #status_area {
        height: 1fr;
        border: solid white;
        padding: 1;
        margin-bottom: 1;
    }

    #message_area {
        height: 1fr;
        border: solid white;
        padding: 1;
    }

    GameDisplay {
        text-style: bold;
        overflow: auto;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("up,w", "move_up", "Move Up"),
        Binding("down,s", "move_down", "Move Down"),
        Binding("left,a", "move_left", "Move Left"),
        Binding("right,d", "move_right", "Move Right"),
        Binding("r", "restart", "Restart"),
        Binding("i", "use_item", "Use Magical Item"),
        Binding("1", "use_elixir", "Use Healing Elixir"),
        Binding("2", "use_scroll", "Use Mystic Scroll"),
    ]

    def __init__(self):
        super().__init__()
        self._initialize_game()

    def _initialize_game(self):
        """Initialize or restart the game."""
        self.game_map = GameMap()
        start_x, start_y = self.game_map.player_start
        self.player = Player(start_x, start_y)

        self.monster_manager = MonsterManager()
        self.combat_system = CombatSystem()
        self.game_state = GameState()
        self.item_manager = ItemManager()

        self.game_map.place_exit()

        monster_count = self.game_state.get_monster_count_for_level()
        item_count = self.game_state.get_item_count_for_level()

        self.monster_manager.spawn_monsters(self.game_map.tiles, monster_count,
                                          self.game_state.current_level)
        self.item_manager.spawn_items(self.game_map.tiles, item_count)

        self.game_map.fov_calculator = FOVCalculator(self.game_map.tiles)
        self.game_map.visibility_tracker = VisibilityTracker()
        self.game_map.update_fov(self.player.x, self.player.y)

    def _advance_to_next_level(self):
        """Advance to the next arcane sanctum."""
        self.game_state.advance_level()

        self.game_map = GameMap()

        start_x, start_y = self.game_map.player_start
        self.player.x = start_x
        self.player.y = start_y

        self.monster_manager = MonsterManager()
        self.item_manager = ItemManager()

        self.game_map.place_exit()

        monster_count = self.game_state.get_monster_count_for_level()
        item_count = self.game_state.get_item_count_for_level()

        self.monster_manager.spawn_monsters(self.game_map.tiles, monster_count,
                                          self.game_state.current_level)
        self.item_manager.spawn_items(self.game_map.tiles, item_count)

        self.game_map.fov_calculator = FOVCalculator(self.game_map.tiles)
        self.game_map.visibility_tracker = VisibilityTracker()
        self.game_map.update_fov(self.player.x, self.player.y)

        game_display = self.query_one(GameDisplay)
        game_display.game_map = self.game_map
        game_display.player = self.player
        game_display.monster_manager = self.monster_manager
        game_display.item_manager = self.item_manager
        game_display.game_state = self.game_state

        self.combat_system.combat_log.append(f"Welcome to Arcane Sanctum {self.game_state.current_level}!")
        self.combat_system.combat_log.append("The magical energies grow more intense...")

    def compose(self) -> ComposeResult:
        """Create the UI layout."""
        yield Header()
        with Horizontal():
            with Container(id="game_area"):
                yield GameDisplay(self.game_map, self.player, self.monster_manager,
                                self.item_manager, self.game_state)
            with Container(id="info_area"):
                with Container(id="status_area"):
                    yield StatusDisplay(self.player, self.game_state)
                with Container(id="message_area"):
                    yield MessageDisplay(self.combat_system)
        yield Footer()

    def action_move_up(self) -> None:
        """Move Arcanist up."""
        self._try_move(0, -1)

    def action_move_down(self) -> None:
        """Move Arcanist down."""
        self._try_move(0, 1)

    def action_move_left(self) -> None:
        """Move Arcanist left."""
        self._try_move(-1, 0)

    def action_move_right(self) -> None:
        """Move Arcanist right."""
        self._try_move(1, 0)

    def action_restart(self) -> None:
        """Restart the current sanctum."""
        current_level = self.game_state.current_level

        self.game_map = GameMap()

        start_x, start_y = self.game_map.player_start
        self.player.x = start_x
        self.player.y = start_y
        self.player.hp = self.player.max_hp

        self.monster_manager = MonsterManager()
        self.item_manager = ItemManager()

        self.game_state.game_over = False
        self.game_state.victory = False
        self.game_state.current_level = current_level

        self.game_map.place_exit()

        monster_count = self.game_state.get_monster_count_for_level()
        item_count = self.game_state.get_item_count_for_level()

        self.monster_manager.spawn_monsters(self.game_map.tiles, monster_count,
                                          self.game_state.current_level)
        self.item_manager.spawn_items(self.game_map.tiles, item_count)

        self.game_map.fov_calculator = FOVCalculator(self.game_map.tiles)
        self.game_map.visibility_tracker = VisibilityTracker()
        self.game_map.update_fov(self.player.x, self.player.y)

        game_display = self.query_one(GameDisplay)
        game_display.game_map = self.game_map
        game_display.player = self.player
        game_display.monster_manager = self.monster_manager
        game_display.item_manager = self.item_manager
        game_display.game_state = self.game_state

        self.combat_system.clear_log()
        self.combat_system.combat_log.append(f"Sanctum {current_level} re-conjured!")

        self.refresh()
        self._update_displays()

    def action_use_item(self) -> None:
        """Open magical item usage menu."""
        self.action_use_elixir()

    def action_use_elixir(self) -> None:
        """Use a healing elixir."""
        result = self.player.inventory.use_item(ItemType.HEALING_ELIXIR, self.player)
        if result:
            self.combat_system.combat_log.append(result)
        else:
            self.combat_system.combat_log.append("No healing elixirs available!")
        self._update_displays()

    def action_use_scroll(self) -> None:
        """Use a mystic scroll."""
        result = self.player.inventory.use_item(ItemType.MYSTIC_SCROLL, self.player)
        if result:
            self.combat_system.combat_log.append(result)
        else:
            self.combat_system.combat_log.append("No mystic scrolls available!")
        self._update_displays()

    def _try_move(self, dx: int, dy: int):
        """Try to move the Arcanist or cast spell if there's a creature.

        Args:
            dx: Change in X coordinate
            dy: Change in Y coordinate
        """
        if self.game_state.game_over:
            return

        new_x = self.player.x + dx
        new_y = self.player.y + dy

        target_monster = self.monster_manager.get_monster_at(new_x, new_y)

        if target_monster and target_monster.is_alive:
            combat_messages = self.combat_system.player_attack_monster(
                self.player, target_monster
            )

            turn_messages = self.combat_system.process_turn(
                self.player, self.monster_manager, self.game_map.tiles,
                self.game_map.visibility_tracker
            )

        elif self.player.move(dx, dy, self.game_map.tiles):
            item = self.item_manager.collect_item(self.player.x, self.player.y)
            if item:
                pickup_message = self.player.inventory.add_item(item)
                self.combat_system.combat_log.append(pickup_message)

            if self.game_state.check_victory_condition(
                self.player.x, self.player.y, self.game_map.tiles
            ):
                self._advance_to_next_level()
                self._update_displays()
                return

            turn_messages = self.combat_system.process_turn(
                self.player, self.monster_manager, self.game_map.tiles,
                self.game_map.visibility_tracker
            )

        self.game_state.check_defeat_condition(self.player)

        self._update_displays()

    def _update_displays(self) -> None:
        """Update all display widgets."""
        self.game_map.update_fov(self.player.x, self.player.y)

        game_display = self.query_one(GameDisplay)
        status_display = self.query_one(StatusDisplay)
        message_display = self.query_one(MessageDisplay)

        game_display.update_display()
        status_display.update_status()
        message_display.update_messages()


def main():
    """Run the magical roguelike game."""
    app = RoguelikeApp()
    app.run()


if __name__ == "__main__":
    main()
