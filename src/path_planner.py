import heapq
import math
import random
from src.location import Location
from src.map_loader import MapLoader
from src.location import Goal


class PathPlanner:
    def __init__(self, map_loader):
        """
        Initialize path planner.
        - map_loader: MapLoader instance with grid data.
        """
        self.map = map_loader
    
    def plan(self, start, goal):
        """
        Generate a path using A* with improved obstacle avoidance.
        - start: Location object (current pose).
        - goal: Goal object (target position).
        Returns: List of (x, y) world coordinates or None if no path.
        """
        start_grid = self.map.world_to_grid(start.x, start.y)
        goal_grid = self.map.world_to_grid(goal.x, goal.y)
        
        print(f"Start: world({start.x}, {start.y}) -> grid{start_grid}")
        print(f"Goal: world({goal.x}, {goal.y}) -> grid{goal_grid}")
        
        # Check if start and goal are valid
        if not self.map.is_valid(*start_grid):
            print(f"Invalid start position {start_grid}. Cell value: {self.map.grid[start_grid[1]][start_grid[0]]}")
            return None
        
        if not self.map.is_valid(*goal_grid):
            print(f"Invalid goal position {goal_grid}. Cell value: {self.map.grid[goal_grid[1]][goal_grid[0]]}")
            return None
        
        # A* algorithm with improved implementation
        open_set = []
        heapq.heappush(open_set, (0, 0, start_grid[0], start_grid[1]))  # (f_score, g_score, x, y)
        came_from = {}
        g_score = {start_grid: 0}
        f_score = {start_grid: self._heuristic(start_grid, goal_grid)}
        closed_set = set()
        
        # 8-directional movement with costs
        directions = [
            (-1, -1, math.sqrt(2)), (-1, 0, 1), (-1, 1, math.sqrt(2)),
            (0, -1, 1),                         (0, 1, 1),
            (1, -1, math.sqrt(2)),  (1, 0, 1),  (1, 1, math.sqrt(2))
        ]
        
        while open_set:
            _, current_g, cx, cy = heapq.heappop(open_set)
            current = (cx, cy)
            
            if current in closed_set:
                continue
            
            closed_set.add(current)
            
            # Check if we reached the goal
            if current == goal_grid:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start_grid)
                path.reverse()
                
                # Convert to world coordinates
                world_path = [self.map.grid_to_world(gx, gy) for gx, gy in path]
                print(f"A* path found with {len(world_path)} waypoints")
                return world_path
            
            # Explore neighbors
            for dx, dy, cost in directions:
                nx, ny = cx + dx, cy + dy
                neighbor = (nx, ny)
                
                if neighbor in closed_set:
                    continue
                
                # Check if neighbor is valid (free space)
                if not self.map.is_valid(nx, ny):
                    continue
                
                # Calculate tentative g_score
                tentative_g = g_score[current] + cost
                
                # If we found a better path to this neighbor
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    h_score = self._heuristic(neighbor, goal_grid)
                    f_score[neighbor] = tentative_g + h_score
                    
                    heapq.heappush(open_set, (f_score[neighbor], tentative_g, nx, ny))
        
        print("A* algorithm: No path found.")
        return None
    
    def _heuristic(self, node, goal):
        """Euclidean distance heuristic."""
        return math.sqrt((node[0] - goal[0])**2 + (node[1] - goal[1])**2)

    def plan_rrt_star(self, start, goal, num_paths=1, max_iter=5000, step_size=0.2, goal_bias=0.1, search_radius=0.5, max_retries=5):
        """
        Generate multiple paths using improved RRT*.
        - start: Location object.
        - goal: Goal object.
        - num_paths: Number of paths to generate.
        - max_iter: Max iterations per run.
        - step_size: Max distance per step (meters).
        - goal_bias: Probability to sample goal.
        - search_radius: Radius for rewiring (meters).
        - max_retries: Retries per path attempt.
        Returns: List of paths (each a list of (x, y)).
        """
        paths = []
        current_iter = max_iter
        
        for attempt in range(num_paths):
            path = None
            retries = 0
            
            while path is None and retries < max_retries:
                # Add slight random offset to start/goal to find different paths
                if attempt > 0:  # Only offset for additional paths
                    offset_x = random.uniform(-0.2, 0.2)
                    offset_y = random.uniform(-0.2, 0.2)
                    start_adj = Location(start.x + offset_x, start.y + offset_y, start.theta)
                    goal_adj = Goal(goal.x + offset_x, goal.y + offset_y)
                else:
                    start_adj = start
                    goal_adj = goal
                
                path = self._rrt_star_single(start_adj, goal_adj, current_iter, step_size, goal_bias, search_radius)
                
                if path is None and current_iter < 20000:
                    current_iter += 2500
                    print(f"Attempt {attempt+1} failed, increasing max_iter to {current_iter}")
                retries += 1
            
            if path:
                paths.append(path)
                print(f"RRT* Path {len(paths)} found with {len(path)} waypoints.")
            else:
                print(f"Failed to find path {attempt+1} after {max_retries} retries.")
        
        if not paths:
            print("Could not generate any RRT* paths. Consider adjusting parameters.")
        
        return paths

    def _rrt_star_single(self, start, goal, max_iter, step_size, goal_bias, search_radius):
        """
        Generate a single path using RRT* with improved collision checking.
        """
        start_node = Node(start.x, start.y)
        goal_node = Node(goal.x, goal.y)
        tree = [start_node]
        
        # Define bounds based on map
        bounds_x = (self.map.origin[0], self.map.origin[0] + self.map.width * self.map.resolution)
        bounds_y = (self.map.origin[1], self.map.origin[1] + self.map.height * self.map.resolution)
        
        print(f"RRT* bounds: X({bounds_x[0]:.2f}, {bounds_x[1]:.2f}), Y({bounds_y[0]:.2f}, {bounds_y[1]:.2f})")
        
        for iteration in range(max_iter):
            # Sample random point or goal
            if random.random() < goal_bias:
                rand_x, rand_y = goal.x, goal.y
            else:
                rand_x = random.uniform(bounds_x[0], bounds_x[1])
                rand_y = random.uniform(bounds_y[0], bounds_y[1])
            rand_node = Node(rand_x, rand_y)
            
            # Find nearest node in tree
            nearest_node = min(tree, key=lambda n: distance(n, rand_node))
            
            # Create new node with step size constraint
            dist = distance(nearest_node, rand_node)
            if dist > step_size:
                theta = math.atan2(rand_node.y - nearest_node.y, rand_node.x - nearest_node.x)
                new_x = nearest_node.x + step_size * math.cos(theta)
                new_y = nearest_node.y + step_size * math.sin(theta)
                new_node = Node(new_x, new_y)
            else:
                new_node = rand_node
            
            # Check if path to new node is collision-free
            if not is_collision_free(self.map, nearest_node, new_node):
                continue
            
            # Find near nodes for rewiring
            near_nodes = [n for n in tree if distance(n, new_node) < search_radius]
            
            # Choose parent with minimum cost
            min_cost_node = nearest_node
            min_cost = nearest_node.cost + distance(nearest_node, new_node)
            
            for near in near_nodes:
                cost = near.cost + distance(near, new_node)
                if cost < min_cost and is_collision_free(self.map, near, new_node):
                    min_cost_node = near
                    min_cost = cost
            
            # Add new node to tree
            new_node.parent = min_cost_node
            new_node.cost = min_cost
            tree.append(new_node)
            
            # Rewire tree
            for near in near_nodes:
                new_cost = new_node.cost + distance(new_node, near)
                if new_cost < near.cost and is_collision_free(self.map, new_node, near):
                    near.parent = new_node
                    near.cost = new_cost
                    # Update costs of all descendants (simplified)
                    self._update_descendants_cost(near)
            
            # Check if we can connect to goal
            if distance(new_node, goal_node) < step_size:
                if is_collision_free(self.map, new_node, goal_node):
                    goal_node.parent = new_node
                    goal_node.cost = new_node.cost + distance(new_node, goal_node)
                    tree.append(goal_node)
                    break
        
        # Extract path if goal was reached
        if goal_node.parent is None:
            return None
        
        # Reconstruct path
        path = []
        current = goal_node
        while current is not None:
            path.append((current.x, current.y))
            current = current.parent
        path.reverse()
        return path
    
    def _update_descendants_cost(self, node):
        """Update costs of all descendants of a node."""
        for child in [n for n in [] if hasattr(n, 'parent') and n.parent == node]:
            child.cost = node.cost + distance(node, child)
            self._update_descendants_cost(child)


class Node:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.cost = 0.0
        self.parent = None


def distance(n1, n2):
    """Calculate Euclidean distance between two nodes."""
    return math.sqrt((n1.x - n2.x)**2 + (n1.y - n2.y)**2)


def is_collision_free(map_loader, n1, n2):
    """
    Check if line between n1 and n2 is free of obstacles with proper collision checking.
    """
    dist = distance(n1, n2)
    
    # If nodes are too close, just check both endpoints
    if dist < map_loader.resolution:
        gx1, gy1 = map_loader.world_to_grid(n1.x, n1.y)
        gx2, gy2 = map_loader.world_to_grid(n2.x, n2.y)
        return map_loader.is_valid(gx1, gy1) and map_loader.is_valid(gx2, gy2)
    
    # Sample points along the line
    steps = max(2, int(dist / (map_loader.resolution * 0.5)))  # High resolution sampling
    
    for i in range(steps + 1):
        t = i / steps if steps > 0 else 0
        interp_x = n1.x + (n2.x - n1.x) * t
        interp_y = n1.y + (n2.y - n1.y) * t
        
        gx, gy = map_loader.world_to_grid(interp_x, interp_y)
        
        # Check bounds and occupancy
        if not (0 <= gx < map_loader.width and 0 <= gy < map_loader.height):
            return False
        
        if not map_loader.is_valid(gx, gy):
            return False
    
    return True