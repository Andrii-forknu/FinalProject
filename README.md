# SandWatch - Animated Hourglass Timer

An elegant and interactive hourglass timer application built with Python's tkinter library. Features realistic sand physics simulation, smooth animations, and a modern user interface.

## Features

- **Realistic Physics**: Individual sand particles with gravity simulation
- **Smooth Animation**: 33 FPS animation for fluid sand movement
- **Interactive Controls**: Start, stop, and resume timer functionality
- **Customizable Duration**: Set timer from 1 second to any desired duration
- **Visual Feedback**: Real-time remaining time display
- **Modern UI**: Clean interface with modern styling

## How It Works

### Core Components

The application consists of three main components:

1. **Particle System**: Individual sand grains represented as `Particle` objects with position and velocity
2. **HourglassCanvas**: Main widget handling all rendering and animation logic
3. **HourglassApp**: Application window with UI controls and styling

### Animation Process

#### 1. Sand Distribution
The hourglass maintains two sand chambers:
- **Top Chamber**: Contains remaining sand as an inverted triangular cone
- **Bottom Chamber**: Accumulates fallen sand in a growing triangular pile

Sand distribution is calculated based on elapsed time vs total duration:
```python
progress = elapsed_time / total_duration
top_fraction = 1.0 - progress      # Remaining sand in top
bottom_fraction = progress         # Accumulated sand in bottom
```

#### 2. Particle Physics
Individual particles simulate falling sand:
- **Generation**: New particles spawn at the neck opening when timer runs
- **Movement**: Particles fall with random velocities (4-8 pixels/frame)
- **Collision**: Particles disappear when hitting the bottom sand pile surface
- **Performance**: Limited to 120 concurrent particles for smooth performance

#### 3. Geometry Calculation
The hourglass shape uses linear interpolation to calculate internal width at any height:
- **Top Chamber**: Triangular shape from wide top to narrow neck
- **Neck Region**: Constant narrow width for sand flow
- **Bottom Chamber**: Triangular shape from narrow neck to wide bottom

#### 4. Rendering Layers
The canvas uses two rendering layers:
- **Static Layer**: Glass outline, frame, and base (drawn once)
- **Dynamic Layer**: Sand masses, particles, and sand stream (redrawn each frame)

### Mathematical Models

#### Sand Height Calculations
- **Top Chamber Height**: `max_height * remaining_fraction`
- **Bottom Chamber Height**: `max_height * accumulated_fraction`

#### Width Interpolation
For any Y coordinate, the internal glass width is calculated using:
```python
width = interpolate_between_boundary_points(y_coordinate)
```

#### Particle Lifecycle
1. **Spawn**: At neck center with random horizontal offset
2. **Fall**: Update position based on velocity each frame  
3. **Collision**: Remove when reaching sand pile surface
4. **Cleanup**: Automatic removal prevents memory buildup

## Installation & Usage

### Requirements
- Python 3.8+ (uses modern type hints with `|` union syntax)
- tkinter (usually included with Python)

### Running the Application
```bash
python SandWatch.py
```

### Controls
- **Duration Field**: Set timer duration in seconds
- **Start Button**: Begin or resume timer
- **Stop Button**: Pause timer (can be resumed)
- **Timer Display**: Shows remaining time in real-time

### Customization
Key parameters can be modified at the top of the file:
```python
CANVAS_W, CANVAS_H = 400, 600      # Window size
TICK_MS = 30                       # Animation speed (30ms = ~33 FPS)
MAX_PARTICLES = 120                # Particle count limit
PARTICLE_RADIUS = 2                # Size of sand grains
FALL_STREAM_WIDTH = 4              # Sand stream thickness
```

## Code Architecture

### Design Patterns
- **Separation of Concerns**: Static vs dynamic rendering
- **State Management**: Clear timer state transitions
- **Performance Optimization**: Particle pooling and cleanup
- **Modern Python**: Type hints, dataclasses, and pattern matching

### Key Methods

#### HourglassCanvas Class
- `start()`: Initialize and begin timer animation
- `stop()`: Pause timer while preserving state
- `animate()`: Main animation loop with frame scheduling
- `update_particles()`: Particle physics simulation
- `draw_static()`: Render unchanging glass elements
- `redraw()`: Update all dynamic visual elements
- `_get_glass_width_at_y()`: Calculate glass internal width
- `draw_sand_top()`: Render top chamber sand cone
- `draw_sand_bottom()`: Render bottom chamber sand pile  
- `draw_falling()`: Render particles and sand stream

#### Performance Features
- **Smart Rendering**: Only redraws dynamic elements each frame
- **Particle Limiting**: Prevents performance degradation
- **Memory Management**: Automatic cleanup of completed particles

## Future Enhancements

Potential improvements for the application:
- Sound effects for sand falling
- Different sand colors/textures
- Multiple hourglass shapes
- Full-screen mode
- Export animation as GIF

## License
MIT License