# Terminus Veil: Chronicles of Emberfall - A Magic Roguelike by Nullsec0x

![banner](./assets/cover.png)

A **magic-themed roguelike** where you play as a wizard exploring ancient dungeons, casting spells, and uncovering arcane secrets.  
Descend through procedurally generated labyrinths filled with magical creatures, powerful artifacts, and forgotten lore.  
This entry in the *Terminus Veil* universe expands upon the series’ foundation with a **deep spell system, mana mechanics, and arcane exploration**.

---

## Features

### Core Gameplay
- **Turn-based exploration and combat** — Move using WASD or arrow keys.
- **Procedural dungeon generation** — Each descent creates a new labyrinth powered by BSP algorithms.
- **Magic system** — Manage mana, cast spells, and harness ancient power.
- **Stat-based progression** — Intelligence and Wisdom influence spell power and regeneration.
- **Resource management** — Mana regenerates slowly, rewarding strategic thinking.
- **Turn-based combat** — Engage enemies using physical attacks or spells.
- **Progressive difficulty** — Enemies grow stronger as you descend deeper.

### Visual Experience
- **Beautiful ASCII Art** — Magical symbols, glowing sigils, and character designs.
- **Smart Wall Rendering** — Uses proper line-drawing characters (╔╗╚╝║═╬) for dungeon realism.
- **Field of View system** — Shadowcasting-based visibility with exploration memory.
- **Color-coded entities** — Distinct hues for players, monsters, and items.
- **Magical atmosphere** — Dynamic environments infused with ley lines and glowing runes.

### Spell System
Master the **four core spells** of Emberfall and manipulate mana to survive.
| Spell | Mana Cost | Effect |
|--------|------------|--------|
| Fireball | 20 MP | Damages the closest visible enemy with fire damage. |
| Heal | 15 MP | Restores 20–35 HP based on Wisdom. |
| Teleport | 25 MP | Instantly move to a random safe location. |
| Lightning Bolt | 30 MP | Strikes a random enemy with high damage. |

### Mage Attributes
- **Intelligence** — Increases spell damage and magical precision.  
- **Wisdom** — Improves healing efficiency and mana regeneration.  
- **Mana Pool** — Regenerates 1 MP per turn naturally.

---

## Magical Entities & Items

### Arcane Creatures
| Symbol | Creature | Description |
|--------|-----------|-------------|
| ♠ | Goblin | Basic enemy, low threat. |
| ♣ | Orc | Strong melee fighter with moderate HP. |
| ♦ | Dragon | Powerful boss enemy with fire breath. |
| ◘ | Arcane Elemental | Magical being that grants mana when defeated. |
| ¶ | Fire Imp | Fire-based creature resistant to burn damage. |
| § | Ice Wraith | Ice-based spirit with freezing attacks. |

### Items & Equipment

#### Consumables
| Item | Symbol | Effect |
|------|---------|--------|
| Health Potion | ♥ | Restores 25 HP. |
| Mana Potion | ♠ | Restores 30 MP. |
| Magic Scroll | ≈ | Triggers a random magical effect. |

#### Equipment
| Item | Symbol | Effect |
|------|---------|--------|
| Magic Wand | ⁄ | +3 Attack, +1 Intelligence. |
| Staff | ⌠ | +20 Max MP, +2 Wisdom. |
| Arcane Amulet | ☼ | +15 Max MP. |

---

## Controls

| Key | Action | Description |
|-----|--------|-------------|
| WASD / Arrows | Move / Attack | Move character or attack with staff. |
| 1 | Cast Fireball | (20 MP) Damages closest enemy. |
| 2 | Cast Heal | (15 MP) Restores HP. |
| 3 | Cast Teleport | (25 MP) Move to safe location. |
| 4 | Cast Lightning Bolt | (30 MP) High damage to random enemy. |
| 5 | Use Mana Potion | Restore 30 MP. |
| 6 | Use Magic Scroll | Random magical effect. |
| R | Restart Level | Restart current level. |
| Q | Quit Game | Exit the game. |

---

## Strategy Guide

### Basic Tips
- **Manage Mana Carefully** — Regeneration is slow, use wisely.
- **Use Teleport** — Great for escaping danger quickly.
- **Heal Proactively** — Don't wait until it’s too late.
- **Collect Mana Potions** — Essential for long runs.

### Advanced Tactics
- Defeating **magical enemies** restores mana.  
- Prioritize boosting **Intelligence** for spell power.  
- **Wisdom** improves mana efficiency and healing potency.  
- Use the **environment** — walls block line of sight for enemies.  

### Spell Combos
- **Fireball → Teleport** — Hit and vanish tactic.  
- **Heal** often between fights to stay alive.  
- **Lightning Bolt** for dangerous targets.  

---

## Installation & Running

### Requirements
- **Python 3.11+**
- **Textualize** library

### Quick Start
```bash
# Install dependencies
pip install textual

# Run the game
python main.py
```

### Building Executable
```bash
pip install pyinstaller
pyinstaller --onefile main.py
```

---

## Project Structure

```
terminus-veil-emberfall/
├── main.py                  # Entry point
├── game/
│   ├── __init__.py
│   ├── player.py            # Mage character and stats
│   ├── game_map.py          # Map rendering and magical terrain
│   ├── dungeon_generator.py # Procedural generation
│   ├── monster.py           # Magical creature system
│   ├── combat.py            # Turn-based combat logic
│   ├── items.py             # Inventory and magical items
│   ├── fov.py               # Field of view
│   ├── ascii_art.py         # Visual rendering
│   ├── magic.py             # Spell system and mana
│   └── spell_effects.py     # Individual spell logic
└── README.md
```

---

## Development & Architecture

- **Engine** — Python + Textualize (TUI framework)  
- **Architecture** — Modular, object-oriented design  
- **Algorithms** — BSP dungeon generation, shadowcasting FOV  
- **Compatibility** — Cross-platform (Windows, macOS, Linux)  

### Development Time (Estimate)
| Phase | Duration | Description |
|--------|-----------|-------------|
| Core Systems | 5 hrs | Player, spells, and mana system |
| Content | 4 hrs | Enemies, items, combat |
| Visual Polish | 3 hrs | ASCII art and UI |

---

## Lore

> In the world of **Emberfall**, magic has reawakened after centuries of silence.  
> Deep within forgotten dungeons, ancient energies stir once more. As a mage of the Arcane Order,  
> you descend into the heart of the world, mastering spells and seeking the truth behind the resurgence of magic itself.  

---

## Contributing

Want to expand Emberfall? You can:  
- Add **new spells and schools of magic**  
- Implement **new character classes** (Sorcerer, Necromancer, etc.)  
- Enhance **magic items** with enchantments  
- Add **bosses** with unique mechanics  

---

## License

**Open source** — Feel free to use and modify.

---

## Credits

Created by **Nullsec0x** as part of the *Terminus Veil* universe.  
Built with Python and **Textualize**, focusing on **arcane adventure** and **magical exploration**.
