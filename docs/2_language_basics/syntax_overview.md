# Syntax Overview

## Basic Principles

NaturalScript is designed to read like natural English while maintaining programming precision. Here are the core syntax rules:

### 1. Command Structure

Commands follow natural English sentence structure:
```
Create a window called "Game"
Set the background to blue
Make the player move left
```

### 2. Indentation and Blocks

Use indentation (4 spaces or tab) to group related commands:
```
Create a player:
    Set position to center
    Set speed to 5
    When space pressed:
        Make player jump
        Play jump sound
```

### 3. Properties and Values

Properties can be set using natural phrases:
```
Set window size to 1280 by 720
Make background color blue
Position player at 100, 200
```

### 4. Events and Conditions

Events use "When" statements:
```
When left mouse button is clicked:
    Create explosion effect

When player health is below 20:
    Show warning message
    Play alert sound
```

### 5. Loops and Repetition

Use natural phrases for repetition:
```
Every frame:
    Update player position
    Check for collisions

Repeat 5 times:
    Create enemy
    Wait 1 second
```

### 6. Variables and References

Reference objects and values naturally:
```
Create score counter with value 0
When player collects coin:
    Add 10 to score counter
    Show score counter on screen
```

### 7. Functions and Behaviors

Define reusable behaviors:
```
Create behavior "Patrol":
    Move right for 2 seconds
    Wait 1 second
    Move left for 2 seconds
    Wait 1 second
    Repeat forever

Add Patrol behavior to guard
```

## Common Syntax Patterns

### Object Creation
```
Create [type] [name] with [properties]:
    [additional settings]
    [behaviors]
```

### Event Handling
```
When [condition]:
    [actions]
```

### Property Setting
```
Set [object] [property] to [value]
Make [object] [property]
```

### Time-Based Actions
```
Every [time period]:
    [actions]

Wait for [duration]
```

## Best Practices

1. **Be Descriptive**
   - Use clear, descriptive names
   - Write complete phrases
   - Avoid abbreviations

2. **Maintain Consistency**
   - Use similar phrases for similar actions
   - Keep indentation consistent
   - Follow natural language patterns

3. **Structure Code Logically**
   - Group related commands together
   - Use appropriate indentation
   - Order commands in a logical sequence