# Getting Started with NaturalScript

## Installation

### System Requirements
- Windows 10/11, macOS 10.15+, or Linux
- 4GB RAM minimum (8GB recommended)
- 2GB free disk space
- Graphics card with OpenGL 3.3+ support

### Installing NaturalScript
1. Download the NaturalScript IDE from our website
2. Run the installer for your operating system
3. Follow the installation wizard
4. Launch NaturalScript IDE

## Your First Project

### Creating a New Project
1. Open NaturalScript IDE
2. Click "New Project" or press Ctrl+N
3. Choose "Basic Game Project"
4. Enter project name and location

### Basic Structure
```
Start a new project called "My First Game"

Create the main window:
    Set size to 800 by 600
    Set title to "Hello World"

Create a blue square:
    Position at center of screen
    Size is 50 pixels

When space key is pressed:
    Make the square jump
```

## Understanding the Basics

### Commands
Commands in NaturalScript are written in plain English:
- "Create" makes new things
- "Set" changes properties
- "When" handles events
- "Make" performs actions

### Indentation
Use indentation to group related commands:
```
Create a button:
    Set text to "Click Me"
    Set color to blue
    When clicked:
        Play sound "beep.wav"
        Change color to red
```

### Common Patterns

#### Creating Objects
```
Create a sprite called "player":
    Use image "player.png"
    Position at 100, 100
    Size is 64 pixels
```

#### Handling Events
```
When left mouse button is clicked:
    Create a sparkle effect
    Play sound "click.wav"
```

#### Regular Updates
```
Every frame:
    Move enemies toward player
    Check for collisions
    Update score display
```

## Common Tasks

### Working with Windows
```
Create a window:
    Set title to "My Window"
    Set size to 1280 by 720
    Use dark theme
```

### Adding Graphics
```
Add image "background.png":
    Stretch to fill window
    Set opacity to 80%
```

### Playing Sounds
```
Play sound "background_music.mp3":
    Set volume to 50%
    Loop forever
```

## Next Steps

1. Explore the [Syntax Overview](../2_language_basics/syntax_overview.md)
2. Learn about [Game Objects](../3_core_concepts/game_objects.md)
3. Try the [Interactive Tutorial](tutorial.md)
4. Join our [Community Forum](https://naturalscript.community)

## Troubleshooting

### Common Issues
- **IDE won't start**: Check system requirements
- **Syntax errors**: Review indentation
- **Missing assets**: Check file paths

### Getting Help
- Use the built-in help (F1)
- Check documentation
- Ask in community forums
- Report bugs on GitHub