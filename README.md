<<<<<<< HEAD

=======
>>>>>>> 5c2f4ff (Switched to docker and termious)
# ROS2 Keyboard to Joy

`keyboard_joy` is a ROS2 package that allows you to simulate joystick input using your keyboard. This is particularly useful for testing and development when a physical joystick is not available.

<<<<<<< HEAD
Tested on ROS2 Humble.

## Installation

1. **Install ROS2**: Follow the official ROS2 installation guide for your operating system.

2. **Install the `pynput` Library**:

   This package requires `pynput` to capture keyboard input. Install it using pip:

   ```bash
   pip3 install pynput
   ```

3. **Clone the `keyboard_joy` Package**:
=======
Works with both X11 and Wayland.

Tested on ROS2 Jazzy.

## Installation

### From Source (Native)

1. **Install ROS2**: Follow the official ROS2 installation guide for your operating system.

2. **Clone the `keyboard_joy` Package**:
>>>>>>> 5c2f4ff (Switched to docker and termious)

   Navigate to your ROS2 workspace's `src` directory and clone the package repository:

   ```bash
   cd ~/your_ros2_workspace/src
   git clone https://github.com/atarbabgei/keyboard_joy.git
   ```

<<<<<<< HEAD
4. **Build the Package**:
=======
3. **Build the Package**:
>>>>>>> 5c2f4ff (Switched to docker and termious)

   Build your workspace to compile the package:

   ```bash
   cd ~/your_ros2_workspace
   colcon build --packages-select keyboard_joy
   ```

<<<<<<< HEAD
5. **Source the Workspace**:
=======
4. **Source the Workspace**:
>>>>>>> 5c2f4ff (Switched to docker and termious)

   Source your workspace to overlay your environment:

   ```bash
   source install/setup.bash
   ```

<<<<<<< HEAD
## Usage

To run the `keyboard_joy` node using the default configuration (as stored in `/config/key_mappings.yaml`), execute the following command:

```bash
ros2 launch keyboard_joy keyboard_joy.launch.py
```

However, if you want to use a custom YAML configuration file for your project, run the following command:

```bash
ros2 launch keyboard_joy keyboard_joy.launch.py config:=/your_path/your_config_file.yaml
```

Replace `/your_path/your_config_file.yaml` with the path to your custom YAML file.

## Configuration

The key mappings for the joystick simulation are configured using a YAML file which allows you to customize which keyboard keys map to specific joystick axes and buttons.

### Example YAML Configuration

```yaml
# Config for mapping keyboard keys to joystick axes and buttons

axes:
  # Axis mappings: Define which keyboard keys control specific joystick axes
  # Format: '<key>: [<axis_index>, <axis_value>, <mode>'
  w: [0, 1.0, 'normal'] 
  s: [0, -1.0, 'normal'] 
  a: [1, 1.0, 'normal']
  d: [1, -1.0, 'normal']
  Key.up: [2, 1.0, 'sticky']   
  Key.down: [2, -1.0, 'sticky']
  Key.left: [3, 1.0, 'sticky']
  Key.right: [3, -1.0, 'sticky']

# Parameters for axis increment_rate, increment_step
parameters:
  axis_increment_rate: 0.01   # Time interval for updating axis values
  axis_increment_step: 0.01   # Step size for axis value change

buttons:
  # Button mappings: Define which keyboard keys toggle specific joystick buttons
  # Format: '<key>: <button_index>'
  '0': 0 
  '1': 1 
  '2': 2 
  '3': 3 
```
=======
### Using Docker

Build the Docker image:

```bash
cd docker
docker compose build
```

Run the container (keep this terminal open to use the keyboard):

```bash
docker compose -f docker/docker-compose.yaml run --rm keyboard_joy
```

To detach from the container without stopping it: press `Ctrl+P` then `Ctrl+Q`.

## Usage

### Native

To run the `keyboard_joy` node using the default configuration (as stored in `config/key_mappings.yaml`), execute the following command:

```bash
ros2 run keyboard_joy joy_node
```

To use a custom YAML configuration file:

```bash
ros2 run keyboard_joy joy_node --ros-args --param config:=/your_path/your_config_file.yaml
```

### Docker

The container runs the node directly. To customize the configuration, use the default config mapping:

```bash
docker compose -f docker/docker-compose.yaml run --rm keyboard_joy --ros-args --param config:=/path/to/config.yaml
```

Note: You need to forward your keyboard input to the container using `-it` (which is automatically enabled with `run --rm`).

## Configuration

All key mappings are **loaded from the YAML config file** (`config/key_mappings.yaml` by default). You can fully customize axes and buttons.

### Default Configuration

The default `key_mappings.yaml` is mapped to work like a standard gamepad (PS4/Xbox style):

```yaml
axes:
  # Left stick (axes 0-1)
  w: [0, 1.0]   # Forward
  s: [0, -1.0]  # Backward
  a: [1, 1.0]  # Left
  d: [1, -1.0]  # Right

  # Right stick (axes 2-3)
  i: [2, 1.0]   # Forward
  k: [2, -1.0]  # Backward
  j: [3, 1.0]  # Left
  l: [3, -1.0]  # Right

buttons:
  # Face buttons (Xbox layout)
  v: 0      # A / Cross (bottom)
  b: 1      # B / Circle (right)
  n: 2      # X / Square (left)
  m: 3      # Y / Triangle (top)

  # Shoulder buttons
  q: 4      # LB / L1
  e: 5      # RB / R1

  # Triggers
  tab: 6    # LT / L2
  caps: 7   # RT / R2

  # Thumb buttons (stick clicks)
  z: 8      # LS / L3
  x: 9      # RS / R3
```

### Configuration Options

**Axes:**
- Format: `'<key>': [<axis_index>, <axis_value>]`
- `<axis_index>`: The joystick axis index (0-3 typically)
- `<axis_value>`: The value to set when pressed (1.0 or -1.0)
- When key is released: axis resets to 0

**Buttons:**
- Format: `'<key>': <button_index>`
- Button indices 0-14 map to standard gamepad buttons
- Press and hold key → button = 1
- Release key → button = 0

### Quick Reference

| Key | Action |
|-----|--------|
| W/S/A/D | Left stick |
| I/K/J/L | Right stick |
| V | A / Cross |
| B | B / Circle |
| N | X / Square |
| M | Y / Triangle |
| Q/E | LB/RB |
| Tab/' | LT/RT |
| Z/X | L3/R3 |
| 1/2/3/4 | D-pad |
| Space | Options |

### Custom Configuration Example

```yaml
axes:
  # Left stick: WASD
  w: [0, 1.0, 'normal']
  s: [0, -1.0, 'normal']
  a: [1, 1.0, 'normal']
  d: [1, -1.0, 'normal']
  # Right stick: IJKL with sticky mode
  i: [2, 1.0, 'sticky']
  k: [2, -1.0, 'sticky']
  j: [3, 1.0, 'sticky']
  l: [3, -1.0, 'sticky']

parameters:
  axis_increment_rate: 0.05
  axis_increment_step: 0.1

buttons:
  space: 0
  enter: 1
  tab: 2
  esc: 3
```
>>>>>>> 5c2f4ff (Switched to docker and termious)
