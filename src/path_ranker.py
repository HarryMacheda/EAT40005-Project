import math

class PathRanker:
    def __init__(self, map_loader, weight_length=0.4, weight_turns=0.3, weight_safety=0.2, weight_smoothness=0.1):
        """
        Initialize PathRanker with improved metrics.
        - map_loader: MapLoader instance for grid conversions and occupancy data.
        - weight_length: Weight for path length (default 0.4).
        - weight_turns: Weight for turn cost (default 0.3).
        - weight_safety: Weight for safety (distance from obstacles) (default 0.2).
        - weight_smoothness: Weight for path smoothness (default 0.1).
        """
        self.map_loader = map_loader
        self.weight_length = weight_length
        self.weight_turns = weight_turns
        self.weight_safety = weight_safety
        self.weight_smoothness = weight_smoothness

    def calculate_length(self, path):
        """
        Calculate total Euclidean distance of the path.
        - path: List of (x, y) coordinates.
        Returns: Float distance in meters.
        """
        if len(path) < 2:
            return 0.0
        
        total_length = 0.0
        for i in range(len(path) - 1):
            dx = path[i + 1][0] - path[i][0]
            dy = path[i + 1][1] - path[i][1]
            total_length += math.sqrt(dx * dx + dy * dy)
        return total_length

    def calculate_turn_cost(self, path):
        """
        Calculate cumulative turning angles (smoother paths have lower turn cost).
        - path: List of (x, y) coordinates.
        Returns: Float cumulative turning angle in radians.
        """
        if len(path) < 3:
            return 0.0
        
        total_turn_cost = 0.0
        
        for i in range(1, len(path) - 1):
            # Vectors for current and next segments
            v1_x = path[i][0] - path[i - 1][0]
            v1_y = path[i][1] - path[i - 1][1]
            v2_x = path[i + 1][0] - path[i][0]
            v2_y = path[i + 1][1] - path[i][1]
            
            # Calculate magnitudes
            mag1 = math.sqrt(v1_x * v1_x + v1_y * v1_y)
            mag2 = math.sqrt(v2_x * v2_x + v2_y * v2_y)
            
            if mag1 * mag2 != 0:  # Avoid division by zero
                # Calculate angle between vectors
                dot_product = v1_x * v2_x + v1_y * v2_y
                cos_theta = dot_product / (mag1 * mag2)
                cos_theta = max(-1.0, min(1.0, cos_theta))  # Clamp for numerical stability
                angle = math.acos(cos_theta)
                
                # Accumulate turning angles (larger angles = higher cost)
                total_turn_cost += angle
        
        return total_turn_cost

    def calculate_safety_cost(self, path):
        """
        Calculate safety cost based on distance to obstacles.
        Paths closer to obstacles have higher cost.
        - path: List of (x, y) coordinates.
        Returns: Float safety cost (higher = less safe).
        """
        if not path:
            return float('inf')
        
        total_safety_cost = 0.0
        safety_radius = 3  # Check within 3 grid cells
        
        for x, y in path:
            gx, gy = self.map_loader.world_to_grid(x, y)
            
            # Find minimum distance to any obstacle
            min_obstacle_distance = float('inf')
            
            for dx in range(-safety_radius, safety_radius + 1):
                for dy in range(-safety_radius, safety_radius + 1):
                    check_x = gx + dx
                    check_y = gy + dy
                    
                    if (0 <= check_x < self.map_loader.width and 
                        0 <= check_y < self.map_loader.height):
                        
                        if self.map_loader.is_occupied(check_x, check_y):
                            obstacle_distance = math.sqrt(dx*dx + dy*dy)
                            min_obstacle_distance = min(min_obstacle_distance, obstacle_distance)
            
            # Convert to safety cost (closer = higher cost)
            if min_obstacle_distance < float('inf'):
                # Use exponential decay: closer obstacles contribute more to cost
                safety_cost = math.exp(-min_obstacle_distance / 2.0)
                total_safety_cost += safety_cost
        
        return total_safety_cost

    def calculate_smoothness_cost(self, path):
        """
        Calculate smoothness cost based on curvature changes.
        - path: List of (x, y) coordinates.
        Returns: Float smoothness cost (higher = less smooth).
        """
        if len(path) < 4:
            return 0.0
        
        total_smoothness_cost = 0.0
        
        for i in range(2, len(path) - 1):
            # Calculate curvature at point i using three consecutive segments
            p1 = path[i - 2]
            p2 = path[i - 1] 
            p3 = path[i]
            p4 = path[i + 1]
            
            # Calculate angles of consecutive segments
            angle1 = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
            angle2 = math.atan2(p3[1] - p2[1], p3[0] - p2[0])
            angle3 = math.atan2(p4[1] - p3[1], p4[0] - p3[0])
            
            # Calculate curvature changes
            curvature1 = self._normalize_angle(angle2 - angle1)
            curvature2 = self._normalize_angle(angle3 - angle2)
            
            # Penalize rapid curvature changes
            curvature_change = abs(curvature2 - curvature1)
            total_smoothness_cost += curvature_change
        
        return total_smoothness_cost
    
    def _normalize_angle(self, angle):
        """Normalize angle to [-pi, pi] range."""
        while angle > math.pi:
            angle -= 2 * math.pi
        while angle < -math.pi:
            angle += 2 * math.pi
        return angle

    def rank_paths(self, paths):
        """
        Rank paths based on weighted scores using improved metrics.
        - paths: List of paths (each a list of (x, y) coordinates).
        Returns: List of (path, score, metrics) tuples, sorted by score (lowest first).
        """
        if not paths:
            return []
        
        ranked_paths = []
        
        # Calculate all metrics first to enable normalization
        all_lengths = []
        all_turns = []
        all_safety = []
        all_smoothness = []
        
        for path in paths:
            if not path:
                continue
            all_lengths.append(self.calculate_length(path))
            all_turns.append(self.calculate_turn_cost(path))
            all_safety.append(self.calculate_safety_cost(path))
            all_smoothness.append(self.calculate_smoothness_cost(path))
        
        if not all_lengths:
            return []
        
        # Normalize metrics to [0, 1] range for fair comparison
        def normalize(values):
            if not values:
                return []
            min_val = min(values)
            max_val = max(values)
            if max_val == min_val:
                return [0.0] * len(values)
            return [(v - min_val) / (max_val - min_val) for v in values]
        
        norm_lengths = normalize(all_lengths)
        norm_turns = normalize(all_turns) 
        norm_safety = normalize(all_safety)
        norm_smoothness = normalize(all_smoothness)
        
        # Calculate weighted scores
        for i, path in enumerate([p for p in paths if p]):
            if i >= len(norm_lengths):
                continue
                
            score = (self.weight_length * norm_lengths[i] + 
                    self.weight_turns * norm_turns[i] + 
                    self.weight_safety * norm_safety[i] + 
                    self.weight_smoothness * norm_smoothness[i])
            
            metrics = {
                'length': all_lengths[i],
                'turn_cost': all_turns[i],
                'safety_cost': all_safety[i],
                'smoothness_cost': all_smoothness[i],
                'normalized_length': norm_lengths[i],
                'normalized_turns': norm_turns[i],
                'normalized_safety': norm_safety[i],
                'normalized_smoothness': norm_smoothness[i]
            }
            
            ranked_paths.append((path, score, metrics))
        
        # Sort by score (lower is better)
        ranked_paths.sort(key=lambda x: x[1])
        
        return ranked_paths
    
    def print_ranking_details(self, ranked_paths):
        """Print detailed ranking information."""
        if not ranked_paths:
            print("No paths to rank.")
            return
        
        print(f"\n{'='*60}")
        print("PATH RANKING DETAILS")
        print(f"{'='*60}")
        print(f"Weights: Length={self.weight_length:.2f}, Turns={self.weight_turns:.2f}, "
              f"Safety={self.weight_safety:.2f}, Smoothness={self.weight_smoothness:.2f}")
        print(f"{'='*60}")
        
        for i, (path, score, metrics) in enumerate(ranked_paths):
            print(f"PATH {i+1} (Score: {score:.3f})")
            print(f"  Length: {metrics['length']:.2f}m (norm: {metrics['normalized_length']:.3f})")
            print(f"  Turn Cost: {metrics['turn_cost']:.2f}rad (norm: {metrics['normalized_turns']:.3f})")
            print(f"  Safety Cost: {metrics['safety_cost']:.2f} (norm: {metrics['normalized_safety']:.3f})")
            print(f"  Smoothness: {metrics['smoothness_cost']:.2f} (norm: {metrics['normalized_smoothness']:.3f})")
            print(f"  Waypoints: {len(path)}")
            print("-" * 40)