# Tomb Bound

A challenging platformer game where you navigate through a dangerous tomb filled with traps and obstacles. Test your reflexes and timing as you explore ancient ruins and avoid deadly hazards.

![Tomb Bound Game](/screenshot/Tomb_Bound.png)

## Game Features

- Dynamic platformer gameplay with increasing difficulty
- Player has three health points - lose one when hit by a trap
- Animated title screen and game over effects
- Score tracking and high score system
- Customizable audio settings
- Pause menu with options
- Atmospheric tomb environment with various obstacles

## Controls

- **Character moves automatically** through the level
- **Space**: Jump
- **ESC**: Pause game/Exit to menu
- **M**: Mute/unmute audio

## Requirements

- Python 3.6 or higher
- Pygame library (2.0.0 or higher recommended)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/YOUR_USERNAME/Tomb_Bound.git
   cd Tomb_Bound
   ```

2. Install the required dependencies:
   ```
   pip install pygame
   ```

3. Run the game:
   ```
   python3 tomb_bound.py
   ```

## Project Structure

- `tomb_bound.py`: Main game file
- `audio_manager.py`: Handles game audio
- `game_over_screen.py`: Game over screen implementation
- `enhanced_title.py`: Title screen implementation
- `game_settings.json`: Game configuration
- Asset directories:
  - `audio/`: Sound effects and music
  - `backgrounds/`: Background images
  - `player/`: Player character sprites
  - `traps/`: Trap and obstacle sprites
  - `decorations/`: UI decorative elements

## Development

The game is built using Python and Pygame, focusing on smooth gameplay and an engaging user experience. The modular code structure makes it easy to extend with new features. Development was assisted by Amazon Q Developer, which helped with code generation, optimization, and debugging.

### Adding New Features

To add new features:
1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Credits

- Game Development: Your Name
- Art Assets: Game Art Sources
- Sound Effects: Audio Libraries

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---
