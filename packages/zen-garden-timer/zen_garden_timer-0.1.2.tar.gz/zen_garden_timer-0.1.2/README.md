# 🌸 Zen Garden

A beautiful CLI productivity timer with growing plants. Your plants grow as you focus, with events occurring every 15 minutes to remind you to take breaks.

## Features

- 🌱 **Real-Time Growth**: Plants animate and grow continuously with smooth transitions
- 🐌 **Adorable Snail**: Watch a snail patrol your garden and collect coins!
- ⏰ **Live Timer**: Real-time countdown to next break event (updates every second)
- ✨ **Smooth Animations**: Plants pulse and change slowly every 2 seconds
- ⌨️ **Instant Keybinds**: Press keys for instant actions (no Enter needed!)
- 🎨 **Beautiful CLI**: Colorful, animated interface that updates in real-time
- 🌺 **5 Plant Types**: Lotus (L), Bamboo (B), Cherry Blossom (C), Bonsai (O), Zen Flower (Z)
- 🪙 **Coin Collection**: Coins spawn randomly and the snail collects them as it patrols
- 📊 **Live Stats**: Track focus time, events, and plant progress in real-time
- 💾 **Auto-Save**: Garden state persists automatically
- ♾️ **Unlimited Plants**: Grow as many plants as you want!

## Installation

Install directly from GitHub:
```bash
pip install git+https://github.com/yourusername/zen_garden.git
```

Or clone and install locally:
```bash
git clone https://github.com/yourusername/zen_garden.git
cd zen_garden
pip install -e .
```

## Usage

Simply run:
```bash
zen
```

## Keybinds

The app responds instantly to keypresses (no Enter needed):

- **M** - Toggle mute (works in any screen)
- **P** - Open plant menu
- **H** or **I** - Toggle help/info
- **Q** - Quit and save garden

When planting (press P first):
- **L** - Plant Lotus 🪷
- **B** - Plant Bamboo 🎋
- **C** - Plant Cherry Blossom 🌸
- **O** - Plant Bonsai 🌳
- **Z** - Plant Zen Flower 🌺
- **X** - Cancel

## How It Works

1. **Real-Time Display**: The garden updates continuously - timer counts down, plants animate
2. **Plant Seeds**: Press P, then choose a plant type with a single key
3. **Watch & Focus**: Plants pulse and animate every 2 seconds while you work
4. **Events**: Every 15 minutes, an event occurs and ALL plants grow one stage
5. **Breaks**: Short breaks every 15 minutes, long breaks every hour (4 events)
6. **Full Bloom**: After 4 hours (16 events/stages), plants reach full bloom!

## Plant Growth Stages

Plants progress through 16 animated stages over 4 hours:

- **Seed** (·○●) - Just planted, pulsing
- **Germinating** (○◌○) - 15 minutes
- **Sprout** (◦╿) - 30-45 minutes
- **Seedling** (ϟ♣) - 1-1.5 hours
- **Growing** (✢❀✿) - 1.5-2.25 hours
- **Maturing** (❁❃) - 2.25-2.75 hours
- **Budding** (❊❋) - 2.75-3 hours
- **Flowering** (✺✻✼) - 3-3.5 hours
- **Full Bloom** (🪷🎋🌸🌳🌺) - 4 hours

Each plant type has unique bloom emoji! Plants animate between frames every 2 seconds.

## Tips

- Leave the app open while you work to track your focus time
- Use the break reminders to rest your eyes and stretch
- Plant multiple seeds to cultivate a full garden
- Your garden state is saved in `~/.zen_garden_data.json`

## Philosophy

Zen Garden combines productivity with mindfulness. Like tending a real garden, growing your digital garden requires patience, consistency, and regular care. Use it as a gentle reminder to balance focus with rest.

🙏 May your garden flourish and your mind find peace.
