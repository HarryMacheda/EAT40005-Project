class Location:
    """Represents a location with x, y coordinates and orientation."""
    
    def __init__(self, x, y, theta):
        self.x = x
        self.y = y
        self.theta = theta

class Goal:
    """Represents a goal position."""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y