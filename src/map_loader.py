import yaml
from PIL import Image
import numpy as np
import os

class MapLoader:
    @classmethod
    def from_yaml(cls, yaml_path):
        """
        Load map from ROS-style YAML and referenced PGM image.
        - yaml_path: Path to the YAML file (e.g., 'maps/my_map.yaml').
        Returns: MapLoader instance.
        """
        with open(yaml_path, 'r') as f:
            params = yaml.safe_load(f)
        
        # Extract parameters
        image_path = params['image']
        if not os.path.isabs(image_path):
            image_path = os.path.join(os.path.dirname(yaml_path), image_path)
        
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Map image not found: {image_path}")
        
        resolution = params['resolution']
        origin = params['origin']  # [x, y, theta]
        negate = params['negate']
        occupied_thresh = params['occupied_thresh']
        free_thresh = params['free_thresh']
        mode = params.get('mode', 'trinary')
        
        # Load PGM image
        img = Image.open(image_path).convert('L')  # Grayscale
        data = np.array(img)  # Shape: (height, width), values 0-255
        
        # Convert to occupancy grid - FIXED INTERPRETATION
        # According to ROS map_server standard:
        # - negate=0 means: black pixels (0) = occupied, white pixels (255) = free
        # - negate=1 means: white pixels (255) = occupied, black pixels (0) = free
        if negate:
            # negate=1: white=occupied, black=free
            prob = data / 255.0  # Higher values (white) = higher probability of occupied
        else:
            # negate=0: black=occupied, white=free  
            prob = (255 - data) / 255.0  # Lower pixel values (black) = higher probability of occupied
        
        grid = np.full(data.shape, -1, dtype=int)  # Default unknown
        if mode == 'trinary':
            grid[prob >= occupied_thresh] = 100  # Occupied
            grid[prob <= free_thresh] = 0       # Free
            # In between remains -1 (unknown)
        
        # Flip vertically to align origin to bottom-left (ROS convention)
        grid = np.flipud(grid)  
        height, width = grid.shape
        
        print(f"Map loaded: {width}x{height}, resolution: {resolution}")
        print(f"Occupied cells: {np.sum(grid == 100)}, Free cells: {np.sum(grid == 0)}, Unknown: {np.sum(grid == -1)}")
        
        return cls(grid.tolist(), resolution, tuple(origin), width, height)
    
    def __init__(self, grid_data, resolution=0.05, origin=(0.0, 0.0, 0.0), width=None, height=None):
        """
        Initialize map.
        - grid_data: 2D list of ints (0=free, 100=occupied, -1=unknown).
        - resolution: Meters per cell.
        - origin: (x, y, theta) in world frame.
        - width, height: Grid dimensions.
        """
        self.grid = grid_data
        self.height = height or len(grid_data)
        self.width = width or (len(grid_data[0]) if grid_data else 0)
        self.resolution = resolution
        self.origin = origin
    
    def is_valid(self, x, y):
        """Check if grid cell (x, y) is within bounds and free (0)."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        cell_value = self.grid[y][x]
        return cell_value == 0  # Only free cells are valid
    
    def is_occupied(self, x, y):
        """Check if grid cell (x, y) is occupied."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return True  # Out of bounds considered occupied
        return self.grid[y][x] == 100
    
    def world_to_grid(self, world_x, world_y):
        """Convert world coordinates to grid indices."""
        grid_x = int((world_x - self.origin[0]) / self.resolution)
        grid_y = int((world_y - self.origin[1]) / self.resolution)
        # Clamp to valid range
        grid_x = max(0, min(grid_x, self.width - 1))
        grid_y = max(0, min(grid_y, self.height - 1))
        return grid_x, grid_y
    
    def grid_to_world(self, grid_x, grid_y):
        """Convert grid indices to world coordinates (center of cell)."""
        world_x = self.origin[0] + (grid_x + 0.5) * self.resolution
        world_y = self.origin[1] + (grid_y + 0.5) * self.resolution
        return world_x, world_y