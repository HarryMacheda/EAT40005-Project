from src import MapLoader, Location, Goal, PathPlanner, PathRanker
import matplotlib.pyplot as plt
import numpy as np
import argparse
import csv

def save_occupancy_coordinates(map_loader, output_file='occupancy_coordinates.csv'):
    """
    Save all world coordinates and occupancy values of the grid to a CSV file.
    - map_loader: MapLoader instance.
    - output_file: Path to save the CSV (default: 'occupancy_coordinates.csv').
    """
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['x', 'y', 'occupancy'])  # Header
        for gy in range(map_loader.height):
            for gx in range(map_loader.width):
                wx, wy = map_loader.grid_to_world(gx, gy)
                occ = map_loader.grid[gy][gx]
                writer.writerow([wx, wy, occ])
    print(f"Occupancy coordinates saved to {output_file}")

def visualize_map(map_loader, paths=None, path_scores=None):
    """
    Enhanced visualization of the occupancy grid map with improved path display.
    - map_loader: MapLoader instance.
    - paths: Optional list of paths (each a list of (x, y)).
    - path_scores: Optional list of path scores for legend.
    """
    grid = np.array(map_loader.grid)
    
    plt.figure(figsize=(15, 12))
    
    # Create custom colormap for occupancy grid
    # -1 (unknown) = gray, 0 (free) = white, 100 (occupied) = black
    cmap = plt.cm.colors.ListedColormap(['gray', 'white', 'black'])
    bounds = [-1.5, -0.5, 50, 100.5]
    norm = plt.cm.colors.BoundaryNorm(bounds, cmap.N)
    
    # Plot occupancy grid with proper orientation
    extent = [
        map_loader.origin[0],
        map_loader.origin[0] + map_loader.width * map_loader.resolution,
        map_loader.origin[1],
        map_loader.origin[1] + map_loader.height * map_loader.resolution
    ]
    
    plt.imshow(grid, cmap=cmap, norm=norm, origin='lower', extent=extent, alpha=0.8)
    plt.colorbar(label='Occupancy (-1=unknown, 0=free, 100=occupied)', ticks=[-1, 0, 100])
    
    # Plot paths if provided
    if paths:
        colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'cyan']
        line_styles = ['-', '--', '-.', ':']
        
        for idx, path in enumerate(paths):
            if path and len(path) > 0:
                path_x, path_y = zip(*path)
                
                color = colors[idx % len(colors)]
                style = line_styles[idx % len(line_styles)]
                
                # Create label with score if available
                if path_scores and idx < len(path_scores):
                    label = f'Path {idx+1} (Score: {path_scores[idx]:.2f})'
                else:
                    label = f'Path {idx+1}'
                
                # Plot path
                plt.plot(path_x, path_y, color=color, linestyle=style, 
                        label=label, linewidth=2.5, alpha=0.8)
                
                # Mark start and goal
                if idx == 0:  # Only mark for first path to avoid clutter
                    plt.plot(path_x[0], path_y[0], 'go', label='Start', 
                            markersize=12, markeredgecolor='darkgreen', markeredgewidth=2)
                    plt.plot(path_x[-1], path_y[-1], 'ro', label='Goal', 
                            markersize=12, markeredgecolor='darkred', markeredgewidth=2)
                
                # Add path direction arrows
                if len(path) > 2:
                    for i in range(0, len(path)-1, max(1, len(path)//5)):  # Show ~5 arrows
                        dx = path_x[i+1] - path_x[i]
                        dy = path_y[i+1] - path_y[i]
                        plt.arrow(path_x[i], path_y[i], dx*0.3, dy*0.3, 
                                head_width=0.05, head_length=0.03, 
                                fc=color, ec=color, alpha=0.6)
        
        plt.legend(bbox_to_anchor=(0.5, -0.05), loc='upper center', ncol=min(3, len(paths)), 
                  bbox_transform=plt.gca().transAxes)
    
    plt.xlabel('X (meters)', fontsize=12)
    plt.ylabel('Y (meters)', fontsize=12)
    title = 'Occupancy Grid Map' if paths is None else f'Path Planning Results ({len(paths)} paths)'
    plt.title(title, fontsize=14, fontweight='bold')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def validate_position(map_loader, x, y, position_name):
    """
    Validate if a world position is in free space.
    - map_loader: MapLoader instance.
    - x, y: World coordinates.
    - position_name: Name for error messages.
    Returns: True if valid, False otherwise.
    """
    gx, gy = map_loader.world_to_grid(x, y)
    
    if not (0 <= gx < map_loader.width and 0 <= gy < map_loader.height):
        print(f"Warning: {position_name} position ({x}, {y}) is outside map bounds.")
        return False
    
    cell_value = map_loader.grid[gy][gx]
    if cell_value != 0:
        print(f"Warning: {position_name} position ({x}, {y}) is in {['unknown', 'free', 'occupied'][min(2, max(0, cell_value//50))]} space (value: {cell_value}).")
        return False
    
    print(f"{position_name} position ({x}, {y}) is valid (free space).")
    return True

def main():
    # Command-line arguments
    parser = argparse.ArgumentParser(description='Enhanced Path Planning with Obstacle Avoidance')
    parser.add_argument('--start_x', type=float, default=0.0, help='Start X position (meters)')
    parser.add_argument('--start_y', type=float, default=0.0, help='Start Y position (meters)')
    parser.add_argument('--goal_x', type=float, default=-1.9, help='Goal X position (meters)')
    parser.add_argument('--goal_y', type=float, default=0.4, help='Goal Y position (meters)')
    parser.add_argument('--save_coords', action='store_true', help='Save occupancy coordinates to CSV')
    parser.add_argument('--visualize_map_only', action='store_true', help='Visualize only the map (no path planning)')
    parser.add_argument('--algorithm', type=str, default='a_star', choices=['a_star', 'rrt_star'], 
                       help='Planning algorithm: a_star or rrt_star')
    parser.add_argument('--num_paths', type=int, default=3, help='Number of paths to generate (for rrt_star)')
    parser.add_argument('--max_iter', type=int, default=5000, help='Maximum iterations for RRT*')
    parser.add_argument('--step_size', type=float, default=0.2, help='Step size for RRT* (meters)')
    parser.add_argument('--no_ranking', action='store_true', help='Skip path ranking')
    
    args = parser.parse_args()
    
    print("="*60)
    print("ROBOT VISION SYSTEM - PATH PLANNING MODULE")
    print("="*60)
    
    # Load map
    try:
        print("Loading map...")
        map_loader = MapLoader.from_yaml('maps/testMap.yaml')
        print(f"Map loaded successfully: {map_loader.width}x{map_loader.height} cells")
        print(f"Resolution: {map_loader.resolution}m/cell")
        print(f"Origin: {map_loader.origin}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure 'maps/my_map.yaml' and 'maps/my_map.pgm' exist in the correct directory.")
        return
    except Exception as e:
        print(f"Unexpected error loading map: {e}")
        return
    
    # Optionally save coordinates
    if args.save_coords:
        save_occupancy_coordinates(map_loader)
    
    # If visualize map only, do that and exit
    if args.visualize_map_only:
        visualize_map(map_loader)
        return
    
    # Validate start and goal positions
    print("\nValidating positions...")
    start_valid = validate_position(map_loader, args.start_x, args.start_y, "Start")
    goal_valid = validate_position(map_loader, args.goal_x, args.goal_y, "Goal")
    
    if not start_valid or not goal_valid:
        print("Error: Invalid start or goal position. Please choose positions in free space (white areas).")
        print("Use --visualize_map_only to see the map and choose valid positions.")
        return
    
    # Define start and goal
    start = Location(x=args.start_x, y=args.start_y, theta=0.0)
    goal = Goal(x=args.goal_x, y=args.goal_y)
    
    print(f"\nPlanning path from ({start.x}, {start.y}) to ({goal.x}, {goal.y})")
    print(f"Algorithm: {args.algorithm.upper()}")
    
    # Plan path(s)
    planner = PathPlanner(map_loader)
    paths = []
    
    if args.algorithm == 'a_star':
        print("Running A* algorithm...")
        path = planner.plan(start, goal)
        if path:
            paths = [path]
            print(f"A* found path with {len(path)} waypoints")
        else:
            print("A* failed to find a path")
    
    else:  # rrt_star
        print(f"Running RRT* algorithm (generating {args.num_paths} paths)...")
        paths = planner.plan_rrt_star(
            start, goal, 
            num_paths=args.num_paths,
            max_iter=args.max_iter,
            step_size=args.step_size
        )
        print(f"RRT* generated {len(paths)} paths")
    
    if not paths:
        print("No paths found! Consider:")
        print("1. Adjusting start/goal positions")
        print("2. Increasing max_iter for RRT*")
        print("3. Checking if start and goal are in free space")
        return
    
    # Rank paths if multiple are generated and ranking is not disabled
    path_scores = None
    if len(paths) > 1 and not args.no_ranking:
        print("\nRanking paths...")
        ranker = PathRanker(map_loader)
        ranked_results = ranker.rank_paths(paths)
        
        if ranked_results:
            # Extract ranked paths and scores
            paths = [result[0] for result in ranked_results]
            path_scores = [result[1] for result in ranked_results]
            
            # Print ranking details
            ranker.print_ranking_details(ranked_results)
        else:
            print("Failed to rank paths")
    
    # Print path summaries
    print(f"\n{'='*60}")
    print("PATH SUMMARY")
    print(f"{'='*60}")
    for idx, path in enumerate(paths):
        length = sum(np.sqrt((path[i+1][0] - path[i][0])**2 + (path[i+1][1] - path[i][1])**2) 
                    for i in range(len(path)-1))
        score_text = f" (Score: {path_scores[idx]:.2f})" if path_scores else ""
        print(f"Path {idx+1}{score_text}: {len(path)} waypoints, {length:.2f}m total length")
    
    # Visualize results
    print(f"\nDisplaying visualization with {len(paths)} path(s)...")
    visualize_map(map_loader, paths, path_scores)
    
    print("Path planning completed successfully!")

if __name__ == "__main__":
    main()