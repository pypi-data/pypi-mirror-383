#!/usr/bin/env python3
"""
Zen Garden - A CLI productivity timer with a persistent garden menu.
"""

import json
import time
import random
import threading
from pathlib import Path
from typing import Dict, List, Optional

import readchar
import pygame

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from rich.live import Live
from rich.align import Align
from rich.layout import Layout
from rich.text import Text

console = Console()

# --- Configuration ---
TEST_MODE = False
EVENT_INTERVAL_SECONDS = 2 if TEST_MODE else 900

# --- Constants ---
PLANT_ANIMATIONS = [
    {"name": "Seed", "frames": ["·", "○", "●"], "color": "dim white", "events": 0},
    {"name": "Germinating", "frames": ["○", "◌", "○"], "color": "white", "events": 1},
    {"name": "Sprout", "frames": ["◦", "◦̇", "◦"], "color": "green", "events": 2},
    {"name": "Early Sprout", "frames": ["╿", "╽", "╿"], "color": "green", "events": 3},
    {"name": "Seedling", "frames": ["ϟ", "Ϡ", "ϟ"], "color": "bright_green", "events": 4},
    {"name": "Young Seedling", "frames": ["♧", "♣", "♧"], "color": "bright_green", "events": 5},
    {"name": "Young Plant", "frames": ["✢", "✣", "✤"], "color": "bright_green", "events": 6},
    {"name": "Growing", "frames": ["❀", "❁", "❀"], "color": "cyan", "events": 7},
    {"name": "Developing", "frames": ["✿", "❀", "✿"], "color": "cyan", "events": 8},
    {"name": "Maturing", "frames": ["❁", "❃", "❁"], "color": "bright_cyan", "events": 9},
    {"name": "Pre-bloom", "frames": ["✾", "❁", "✾"], "color": "magenta", "events": 10},
    {"name": "Budding", "frames": ["❊", "❋", "❊"], "color": "magenta", "events": 11},
    {"name": "Early Bloom", "frames": ["✺", "✻", "✺"], "color": "bright_magenta", "events": 12},
    {"name": "Flowering", "frames": ["✼", "✽", "✼"], "color": "bright_magenta", "events": 13},
    {"name": "Full Flower", "frames": ["❀", "✿", "❁"], "color": "bright_magenta", "events": 14},
    {"name": "Peak Bloom", "frames": ["✾", "❁", "✾"], "color": "yellow", "events": 15},
]

PLANT_TYPES = {
    "lotus": {"name": "Lotus", "bloom": "🪷", "color": "magenta", "key": "l"},
    "bamboo": {"name": "Bamboo", "bloom": "🎋", "color": "green", "key": "b"},
    "cherry": {"name": "Cherry Blossom", "bloom": "🌸", "color": "pink", "key": "c"},
    "bonsai": {"name": "Bonsai", "bloom": "🌳", "color": "bright_green", "key": "o"},
    "zen_flower": {"name": "Zen Flower", "bloom": "🌺", "color": "bright_magenta", "key": "z"}
}

EVENT_MESSAGES = {
    "short_break": [
        "🧛 Break Time Bludsucka !",
        "🔇 Joe Biden Man",
        "🥳 Where da faq the short break ? Here it is !!",
        "😍 Time For a Break Finnashawty"
    ],
    "long_break": [
        "🌟 Go Stretch em Legs Thugga",
        "🙋‍♀️ I use Arch Btw >:-)"
    ]
}

DATA_FILE = Path.home() / ".zen_garden_data.json"

# Snail and coin constants
SNAIL_EMOJI = "🐌"
COIN_EMOJI = "🪙"
SNAIL_SPEED = 0.2  # Cells per update
COIN_SPAWN_CHANCE = 0.004  # 0.8% chance per update


class Coin:
    """Represents a collectible coin."""

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y


class Snail:
    """The adorable snail that collects coins."""

    def __init__(self):
        self.x = 15
        self.y = 15
        self.direction = 0  # 0=right, 1=down, 2=left, 3=up
        self.coins_collected = 0
        self.last_move_time = time.time()

    def move(self, terminal_width: int, terminal_height: int):
        """Move the snail along the screen edges in a wide rectangle."""
        current_time = time.time()
        if current_time - self.last_move_time < 0.03:  # Move every 0.03 seconds
            return

        self.last_move_time = current_time

        # Move in a rectangle with 15-char margin from edges
        margin = 15

        # Move in current direction
        if self.direction == 0:  # Moving right along top
            self.x += SNAIL_SPEED
            if self.x >= terminal_width - margin:
                self.direction = 1  # Turn down
                self.x = terminal_width - margin  # Clamp to edge
        elif self.direction == 1:  # Moving down along right
            self.y += SNAIL_SPEED
            if self.y >= terminal_height - margin:
                self.direction = 2  # Turn left
                self.y = terminal_height - margin  # Clamp to edge
        elif self.direction == 2:  # Moving left along bottom
            self.x -= SNAIL_SPEED
            if self.x <= margin:
                self.direction = 3  # Turn up
                self.x = margin  # Clamp to edge
        elif self.direction == 3:  # Moving up along left
            self.y -= SNAIL_SPEED
            if self.y <= margin:
                self.direction = 0  # Turn right
                self.y = margin  # Clamp to edge

    def check_coin_collision(self, coins: List[Coin]) -> List[Coin]:
        """Check if snail is touching any coins and remove them."""
        remaining_coins = []
        for coin in coins:
            # Check if snail is within 3 cells of the coin (larger radius to account for fractional movement)
            if abs(self.x - coin.x) <= 3 and abs(self.y - coin.y) <= 3:
                self.coins_collected += 1
            else:
                remaining_coins.append(coin)
        return remaining_coins


class SnailManager:
    """Manages the snail and coins system."""

    def __init__(self):
        self.snail = Snail()
        self.coins: List[Coin] = []
        self.last_coin_spawn = time.time()

    def update(self, terminal_width: int, terminal_height: int):
        """Update snail position and spawn coins."""
        self.snail.move(terminal_width, terminal_height)

        # Spawn new coins randomly
        if random.random() < COIN_SPAWN_CHANCE:
            self.spawn_coin(terminal_width, terminal_height)

        # Check for coin collisions
        self.coins = self.snail.check_coin_collision(self.coins)

    def spawn_coin(self, terminal_width: int, terminal_height: int):
        """Spawn a new coin at a random edge location, far from center panel."""
        edge = random.randint(0, 3)  # 0=top, 1=right, 2=bottom, 3=left

        # Spawn coins much further from the panel (in the outer margins)
        margin = 15

        if edge == 0:  # Top edge
            x = random.randint(margin, terminal_width - margin)
            y = margin
        elif edge == 1:  # Right edge
            x = terminal_width - margin
            y = random.randint(margin, terminal_height - margin)
        elif edge == 2:  # Bottom edge
            x = random.randint(margin, terminal_width - margin)
            y = terminal_height - margin
        else:  # Left edge
            x = margin
            y = random.randint(margin, terminal_height - margin)

        self.coins.append(Coin(x, y))


class MusicPlayer:
    """Handles background music playback."""

    def __init__(self, music_file: str):
        self.is_initialized = False
        if Path(music_file).exists():
            try:
                pygame.init()
                pygame.mixer.init()
                pygame.mixer.music.load(music_file)
                self.is_initialized = True
            except Exception:
                pass

    def play_in_background(self):
        if self.is_initialized:
            threading.Thread(
                target=lambda: pygame.mixer.music.play(loops=-1),
                daemon=True
            ).start()

    def stop(self):
        if self.is_initialized:
            pygame.mixer.music.stop()


class Plant:
    """Represents a plant with growth stages and animations."""

    def __init__(self, plant_type: str, planted_at: Optional[float] = None):
        self.type = plant_type
        self.planted_at = planted_at or time.time()
        self.events_completed = 0
        self.animation_frame = 0
        self.last_frame_update = time.time()
        self.last_event_time = time.time()

    def get_stage(self) -> Dict:
        """Get current growth stage based on events completed."""
        for stage in reversed(PLANT_ANIMATIONS):
            if self.events_completed >= stage["events"]:
                return stage
        return PLANT_ANIMATIONS[0]

    def is_fully_grown(self) -> bool:
        return self.events_completed >= PLANT_ANIMATIONS[-1]["events"]

    def update_animation(self):
        """Update animation frame every 2 seconds."""
        if time.time() - self.last_frame_update >= 2.0:
            stage = self.get_stage()
            self.animation_frame = (self.animation_frame + 1) % len(stage["frames"])
            self.last_frame_update = time.time()

    def get_visual(self, in_session: bool = True) -> str:
        """Get visual representation of the plant."""
        if not in_session or self.is_fully_grown():
            return PLANT_TYPES[self.type]["bloom"]

        stage = self.get_stage()
        frame = stage["frames"][self.animation_frame]
        return f"[{stage['color']}]{frame}[/{stage['color']}]"

    def get_progress(self) -> float:
        """Calculate growth progress as percentage."""
        max_events = PLANT_ANIMATIONS[-1]["events"] + 1
        return min(100, (self.events_completed / max_events) * 100)

    def check_for_event(self) -> Optional[str]:
        """Check if an event should occur and return event type."""
        if time.time() - self.last_event_time >= EVENT_INTERVAL_SECONDS:
            self.last_event_time = time.time()
            if not self.is_fully_grown():
                self.events_completed += 1

            is_long_break = (self.events_completed > 0 and
                           self.events_completed % 4 == 0)
            return "long_break" if is_long_break else "short_break"
        return None

    def get_time_until_next_event(self) -> int:
        """Get remaining time until next event in seconds."""
        elapsed = time.time() - self.last_event_time
        return max(0, int(EVENT_INTERVAL_SECONDS - elapsed))

    def to_dict(self) -> Dict:
        return {
            "type": self.type,
            "planted_at": self.planted_at,
            "events_completed": self.events_completed
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Plant':
        plant = cls(data["type"], data["planted_at"])
        plant.events_completed = data.get("events_completed", 0)
        return plant


class ZenGarden:
    """Manages the collection of completed plants."""

    def __init__(self):
        self.plants: List[Plant] = []
        self.load_data()

    def save_data(self):
        """Persist garden data to disk."""
        data = {"plants": [p.to_dict() for p in self.plants]}
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def load_data(self):
        """Load garden data from disk."""
        if DATA_FILE.exists():
            try:
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
                self.plants = [Plant.from_dict(p) for p in data.get("plants", [])]
            except Exception:
                pass

    def add_completed_plant(self, plant: Plant):
        """Add a fully grown plant to the garden."""
        self.plants.append(plant)
        self.save_data()


class GardenApp:
    """Main application controller."""

    def __init__(self):
        self.garden = ZenGarden()
        self.running = True
        self.app_state = 'menu'
        self.last_key_pressed = None
        self.session_plant = None
        self.session_running = False
        self.last_event_message = None
        self.event_message_time = None
        self.snail_manager = SnailManager()
        self.key_listener_thread = threading.Thread(
            target=self._key_listener,
            daemon=True
        )

    def _key_listener(self):
        """Background thread to listen for key presses."""
        while self.running:
            try:
                self.last_key_pressed = readchar.readkey()
            except KeyboardInterrupt:
                self.running = False

    def _handle_input(self):
        """Process keyboard input based on current state."""
        if self.last_key_pressed is None:
            return

        key = self.last_key_pressed.lower()
        self.last_key_pressed = None

        if self.app_state == 'menu':
            if key == 's':
                self.app_state = 'selecting_plant'
            elif key == 'q':
                self.running = False

        elif self.app_state == 'selecting_plant':
            if key == 'q':
                self.app_state = 'menu'
            else:
                for plant_type, info in PLANT_TYPES.items():
                    if key == info['key']:
                        self.start_session(plant_type)
                        break

        elif self.app_state == 'session':
            if key == 'q':
                self.session_running = False

    def _create_garden_display(self) -> Panel:
        """Create the main garden menu display."""
        grid = Table.grid(expand=False)
        grid.add_column(justify="center", no_wrap=False, width=70)

        # Title
        title = Text("🌸 Z E N   G A R D E N 🌸", style="bold bright_green")
        grid.add_row(title)

        subtitle = Text("Cultivate focus, nurture peace.", style="dim")
        grid.add_row(subtitle)
        grid.add_row("")

        # Garden display
        if not self.garden.plants:
            grid.add_row("Your garden is empty.")
            grid.add_row("Complete a session to grow your first plant!")
        else:
            # Show plants
            plants = Text()
            for i, p in enumerate(self.garden.plants):
                if i > 0:
                    plants.append("  ", style="")
                plants.append(p.get_visual(in_session=False), style="")
            grid.add_row(plants)

        grid.add_row("")
        controls = Text("Press [S] to start | Press [Q] to quit", style="bold")
        grid.add_row(controls)

        return Panel(
            grid,
            border_style="green",
            box=box.ROUNDED,
            padding=(2, 4)
        )

    def _create_plant_selection_display(self) -> Panel:
        """Create the plant selection menu."""
        grid = Table.grid(expand=False)
        grid.add_column(justify="center", no_wrap=False, width=70)

        header = Text("Choose a seed to cultivate:", style="bold green")
        grid.add_row(header)
        grid.add_row("")

        for _, info in PLANT_TYPES.items():
            line = Text(f"  Press [{info['key'].upper()}] for {info['bloom']} {info['name']}", style="")
            grid.add_row(line)

        grid.add_row("")
        footer = Text("Press [Q] to return to the Garden.", style="")
        grid.add_row(footer)

        return Panel(
            grid,
            border_style="cyan",
            padding=(2, 4),
            box=box.ROUNDED
        )

    def _create_session_display(self) -> Panel:
        """Create the zen session display."""
        # Use Table.grid for better layout control
        grid = Table.grid(expand=False)
        grid.add_column(justify="center", no_wrap=False, width=70)

        # Title
        title = Text()
        title.append("🌸 Z E N   S E S S I O N 🌸", style="bold cyan")
        grid.add_row(title)
        grid.add_row("")

        subtitle = Text("Focus on the present moment", style="dim")
        grid.add_row(subtitle)
        grid.add_row("")

        # Timer
        time_remaining = self.session_plant.get_time_until_next_event()
        minutes, seconds = divmod(time_remaining, 60)

        timer = Text()
        if self.session_plant.is_fully_grown():
            timer.append("🎉 Session Complete!", style="bold green")
        else:
            break_num = (self.session_plant.events_completed % 4) + 1
            timer.append(f"⏱️ {minutes:02d}:{seconds:02d}", style="bold yellow")
            if break_num == 4:
                timer.append(" → Long Break", style="magenta")
            else:
                timer.append(f" → Break {break_num}/4", style="green")

        grid.add_row(timer)
        grid.add_row("")

        # Event message (only show for 5 seconds after event)
        if (self.last_event_message and self.event_message_time and
            time.time() - self.event_message_time < 5):
            event = Text()
            event.append("✨ ", style="bold yellow")
            event.append(self.last_event_message, style="bold yellow")
            grid.add_row(event)
            grid.add_row("")

        # Plant info
        p_info = PLANT_TYPES[self.session_plant.type]
        plant_visual = self.session_plant.get_visual()
        stage_name = self.session_plant.get_stage()['name']

        plant_info = Text()
        visual_text = Text.from_markup(plant_visual)
        plant_info.append(visual_text)
        plant_info.append(f"  {p_info['name']} - {stage_name}", style="")
        grid.add_row(plant_info)

        # Progress bar
        progress = self.session_plant.get_progress()
        bar_length = 20
        filled = int(progress / 100 * bar_length)
        bar_text = Text()
        bar_text.append("█" * filled + "░" * (bar_length - filled), style=p_info['color'])
        bar_text.append(f" {progress:.0f}%", style="")
        grid.add_row(bar_text)

        grid.add_row("")
        quit_text = Text("Press [Q] to quit early", style="dim")
        grid.add_row(quit_text)

        return Panel(
            grid,
            border_style="cyan",
            box=box.ROUNDED,
            padding=(2, 4)
        )

    def _create_transition_display(self, message: str, message_style: str = "bold green") -> Panel:
        """Create a centered transition message display."""
        grid = Table.grid(expand=False)
        grid.add_column(justify="center", no_wrap=False, width=70)

        msg = Text(message, style=message_style)
        grid.add_row(msg)

        return Panel(
            grid,
            border_style="cyan",
            box=box.ROUNDED,
            padding=(2, 4)
        )

    def _create_display_with_snail(self, base_panel):
        """Add snail and coins around the base panel with precise positioning."""
        term_width = console.width
        term_height = console.height

        # Update snail and coins
        self.snail_manager.update(term_width, term_height)

        snail = self.snail_manager.snail

        # Create main container with 3 rows (top, middle, bottom)
        container = Table.grid(expand=False)
        container.add_column(justify="center")

        margin = 15

        # Divide screen into 3 vertical zones to show snail only once
        panel_area_top = margin + 8
        panel_area_bottom = term_height - margin - 8

        # TOP ROW - show snail/coins only if in top zone
        # Use a fixed-width area to prevent shifting
        top_grid = Table.grid(expand=False)
        top_grid.add_column(justify="center", width=80)
        top_text = Text()

        # Check if snail is in top zone
        if snail.y < panel_area_top:
            # Map snail's x position to display position (0-80 chars)
            display_x = int((snail.x / term_width) * 78)
            top_text.append(" " * display_x + SNAIL_EMOJI)

        # Add coins in top zone (only one coin per zone)
        top_coins = [c for c in self.snail_manager.coins if c.y < panel_area_top]
        if top_coins and not (snail.y < panel_area_top):  # Only show if snail not in this zone
            coin = top_coins[0]  # Show first coin only
            display_x = int((coin.x / term_width) * 78)
            top_text.append(" " * max(0, display_x - len(top_text)) + COIN_EMOJI)

        top_grid.add_row(top_text)
        container.add_row(top_grid)

        # MIDDLE ROW - panel with fixed side margins
        middle_grid = Table.grid(expand=False)
        middle_grid.add_column(width=15, justify="center")  # Fixed left margin
        middle_grid.add_column(justify="center")  # Panel
        middle_grid.add_column(width=15, justify="center")  # Fixed right margin

        # Left margin - show snail if on left side in middle zone
        left_text = Text()
        if panel_area_top <= snail.y < panel_area_bottom and snail.x < term_width // 2:
            # Calculate vertical position within the margin area
            relative_y = int((snail.y - panel_area_top) / ((panel_area_bottom - panel_area_top) / 12))
            relative_y = max(0, min(11, relative_y))
            for i in range(12):
                if i == relative_y:
                    left_text.append(SNAIL_EMOJI + "\n")
                else:
                    left_text.append("\n")

        # Right margin - show snail if on right side in middle zone
        right_text = Text()
        if panel_area_top <= snail.y < panel_area_bottom and snail.x >= term_width // 2:
            # Calculate vertical position
            relative_y = int((snail.y - panel_area_top) / ((panel_area_bottom - panel_area_top) / 12))
            relative_y = max(0, min(11, relative_y))
            for i in range(12):
                if i == relative_y:
                    right_text.append(SNAIL_EMOJI + "\n")
                else:
                    right_text.append("\n")

        middle_grid.add_row(left_text, base_panel, right_text)
        container.add_row(middle_grid)

        # BOTTOM ROW - show snail/coins only if in bottom zone
        bottom_grid = Table.grid(expand=False)
        bottom_grid.add_column(justify="center", width=80)
        bottom_text = Text()

        # Check if snail is in bottom zone
        if snail.y >= panel_area_bottom:
            # Map snail's x position to display position
            display_x = int((snail.x / term_width) * 78)
            bottom_text.append(" " * display_x + SNAIL_EMOJI)

        # Add coins in bottom zone (only one coin per zone)
        bottom_coins = [c for c in self.snail_manager.coins if c.y >= panel_area_bottom]
        if bottom_coins and not (snail.y >= panel_area_bottom):  # Only show if snail not in this zone
            coin = bottom_coins[0]  # Show first coin only
            display_x = int((coin.x / term_width) * 78)
            bottom_text.append(" " * max(0, display_x - len(bottom_text)) + COIN_EMOJI)

        bottom_grid.add_row(bottom_text)
        container.add_row(bottom_grid)

        # Coin counter
        container.add_row(Text(
            f"\n🐌 Coins: {snail.coins_collected}",
            style="dim yellow",
            justify="center"
        ))

        return container

    def _run_menu_loop(self):
        """Run the main menu loop."""
        layout = Layout()
        layout.update(Align.center(self._create_garden_display(), vertical="middle"))

        with Live(layout, console=console, screen=True, refresh_per_second=4) as live:
            while self.running and self.app_state == 'menu':
                self._handle_input()
                layout.update(
                    Align.center(self._create_garden_display(), vertical="middle")
                )
                time.sleep(0.25)

    def _run_selection_loop(self):
        """Run the plant selection loop."""
        layout = Layout()
        layout.update(
            Align.center(self._create_plant_selection_display(), vertical="middle")
        )

        with Live(layout, console=console, screen=True, refresh_per_second=4) as live:
            while self.running and self.app_state == 'selecting_plant':
                self._handle_input()
                layout.update(
                    Align.center(self._create_plant_selection_display(), vertical="middle")
                )
                time.sleep(0.25)

    def start_session(self, plant_type: str):
        """Initialize a new zen session."""
        self.session_plant = Plant(plant_type)
        self.session_running = True
        self.last_event_message = None
        self.event_message_time = None
        self.app_state = 'session'

    def _run_session_loop(self):
        """Run the zen session loop."""
        layout = Layout()

        with Live(layout, console=console, screen=True, refresh_per_second=30) as live:
            while self.session_running and not self.session_plant.is_fully_grown():
                self._handle_input()
                self.session_plant.update_animation()

                # Check for events
                event_type = self.session_plant.check_for_event()
                if event_type:
                    self.last_event_message = random.choice(
                        EVENT_MESSAGES[event_type]
                    )
                    self.event_message_time = time.time()

                # Update display with snail and coins
                base_panel = self._create_session_display()
                display = self._create_display_with_snail(base_panel)
                layout.update(Align.center(display, vertical="middle"))
                time.sleep(0.033)

            # Show transition message within Live context (without snail)
            if self.session_plant.is_fully_grown():
                self.garden.add_completed_plant(self.session_plant)
                transition = Align.center(
                    self._create_transition_display(
                        "Well done! Your plant was added to your garden.",
                        "bold green"
                    ),
                    vertical="middle"
                )
            else:
                transition = Align.center(
                    self._create_transition_display(
                        "Session ended early. Your plant did not bloom.",
                        "yellow"
                    ),
                    vertical="middle"
                )

            layout.update(transition)
            time.sleep(2.5)

        # Small delay for clean transition
        time.sleep(0.2)
        self.app_state = 'menu'

    def run(self):
        """Start the application."""
        self.key_listener_thread.start()
        try:
            while self.running:
                if self.app_state == 'menu':
                    self._run_menu_loop()
                elif self.app_state == 'selecting_plant':
                    self._run_selection_loop()
                elif self.app_state == 'session':
                    self._run_session_loop()
        finally:
            self.running = False


def main():
    """Application entry point."""
    music_player = MusicPlayer("background_music.mp3")
    try:
        music_player.play_in_background()
        app = GardenApp()
        app.run()
        console.print(
            "\n[green]🙏 Your garden is saved. Until we meet again...[/green]\n"
        )
    except Exception as e:
        console.print(f"\n[red]An unexpected error occurred: {e}[/red]\n")
    finally:
        music_player.stop()


if __name__ == "__main__":
    main()
