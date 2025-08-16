# Robot Vision System for Safe Navigation in a Warehouse

## Overview

This project implements a robot vision system designed for safe navigation in a warehouse environment. It features path planning using A* and RRT* algorithms, supporting obstacle avoidance, multiple path generation, and path ranking. The system is compatible with ROS for map visualization and uses YAML and PGM formats for map configuration.

## Features

- **A\* Path Planning**: Computes the shortest path from start to goal coordinates.
- **RRT\* Path Planning**: Generates multiple path options with configurable parameters.
- **Obstacle Avoidance**: Ensures paths avoid obstacles using occupancy grid data.
- **Path Accuracy Scoring**: Evaluates and ranks generated paths based on accuracy.
- **Map Visualization**: Supports visualization of warehouse maps in ROS-compatible YAML + PGM formats.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/HarryMacheda/EAT40005-Project/tree/path-planning.git
   ```
2. Navigate to the project directory:
   ```bash
   cd robot-vision-path-planning
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### A\* Path Planning

To compute the shortest path using the A\* algorithm:

```bash
python main.py --start_x 0 --start_y 0 --goal_x 2 --goal_y 3
```

### RRT\* Multiple Paths

To generate multiple paths using the RRT\* algorithm:

```bash
python main.py --algorithm rrt_star --num_paths 5 --start_x 0 --start_y 0 --goal_x 3 --goal_y 2
```

### Visualize Map

To visualize the warehouse map without running path planning:

```bash
python main.py --visualize_map_only
```

## Arguments

| Option        | Description                                      |
| ------------- | ------------------------------------------------ |
| `--start_x`   | Start x-coordinate (meters)                      |
| `--start_y`   | Start y-coordinate (meters)                      |
| `--goal_x`    | Goal x-coordinate (meters)                       |
| `--goal_y`    | Goal y-coordinate (meters)                       |
| `--algorithm` | Path planning algorithm (`a_star` or `rrt_star`) |
| `--num_paths` | Number of paths to generate (RRT\* only)         |
| `--max_iter`  | Maximum iterations (RRT\* only)                  |
| `--step_size` | Step size in meters (RRT\* only)                 |

## Map Format

- **YAML**: Defines map configuration, including resolution and occupancy thresholds.
- **PGM**: Represents the occupancy grid, where white pixels indicate free space and black pixels indicate occupied space (obstacles).

## Footer

© 2025 GitHub, Inc.
