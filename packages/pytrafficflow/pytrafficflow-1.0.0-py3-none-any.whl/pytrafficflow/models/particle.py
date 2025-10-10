"""
Simple particle-based traffic model
Implements the initial model from Section 2 that optimizes for speed
"""

import numpy as np
from core.vehicle import ParticleCar

class ParticleTrafficModel(ParticleCar):
    """
    Simple particle-based traffic model (Section 2)
    Cars optimize for speed according to Equation 3
    """
    
    def __init__(self, L, vmax, dmin, lcar, dt=1/3600):
        """
        Parameters:
        -----------
        L : float
            Road length (km)
        vmax : float
            Maximum speed (km/h)
        dmin : float
            Minimum safe distance (km)
        lcar : float
            Car length (km)
        dt : float
            Time step (hours), default is 1 second
        """
        self.L = L
        self.vmax = vmax
        self.dmin = dmin
        self.lcar = lcar
        self.dt = dt
        self.cars = []
        self.time = 0.0
        
    def add_car(self, position, velocity):
        """
        Add a car to the road
        
        Parameters:
        -----------
        position : float
            Initial position (km)
        velocity : float
            Initial velocity (km/h)
        """
        car = ParticleCar(position, velocity)
        self.cars.append(car)
        # Keep cars sorted by position (descending order)
        self.cars.sort(key=lambda c: c.x, reverse=True)
        
    def compute_velocity_simple(self, car_idx):
        """
        Compute velocity using simple model from Equation 3
        
        Parameters:
        -----------
        car_idx : int
            Index of the car
            
        Returns:
        --------
        v_desired : float
            Desired velocity to maintain dmin spacing
        """
        if car_idx == 0:
            # First car (front) - no car ahead, drive at max speed
            return self.vmax
        
        car = self.cars[car_idx]
        front_car = self.cars[car_idx - 1]
        
        # Equation 3: maximize speed while maintaining dmin
        v_desired = max(0, min(
            (front_car.x - car.x - self.dmin + front_car.v * self.dt) / self.dt,
            self.vmax
        ))
        
        return v_desired
    
    def step(self):
        """
        Advance simulation one time step
        """
        # Update velocities for all cars
        for i, car in enumerate(self.cars):
            car.v = self.compute_velocity_simple(i)
        
        # Update positions
        for car in self.cars:
            car.x += car.v * self.dt
        
        # Remove cars that have left the road
        self.cars = [c for c in self.cars if c.x <= self.L]
        
        # Update time
        self.time += self.dt
    
    def get_positions(self):
        """Get current positions of all cars"""
        return [car.x for car in self.cars]
    
    def get_velocities(self):
        """Get current velocities of all cars"""
        return [car.v for car in self.cars]
    
    def get_density_at(self, x, window=0.1):
        """
        Compute local density around position x
        
        Parameters:
        -----------
        x : float
            Position to measure density
        window : float
            Window size (km)
            
        Returns:
        --------
        rho : float
            Local density
        """
        cars_in_window = sum(1 for car in self.cars 
                           if x - window/2 <= car.x <= x + window/2)
        return (cars_in_window * self.lcar) / window