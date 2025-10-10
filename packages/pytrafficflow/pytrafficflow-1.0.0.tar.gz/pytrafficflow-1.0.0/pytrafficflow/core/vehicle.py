class ParticleCar:
    """
    Represents a single car in the particle-based model
    """
    
    def __init__(self, position, velocity, acceleration=0):
        """
        Parameters:
        -----------
        position : float
            Position on road (km)
        velocity : float
            Current velocity (km/h)
        acceleration : float
            Current acceleration (m/s²)
        """
        self.x = position
        self.v = velocity
        self.a = acceleration