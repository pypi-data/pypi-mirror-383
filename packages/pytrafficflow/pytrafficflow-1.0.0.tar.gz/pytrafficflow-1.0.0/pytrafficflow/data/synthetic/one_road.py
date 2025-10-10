"""
Traffic Simulation using Intelligent Driver Model (IDM)
A Python implementation inspired by traffic-simulation.de

# https://traffic-simulation.de/
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Rectangle
from dataclasses import dataclass
from typing import List, Optional
import matplotlib.patches as mpatches

@dataclass
class Vehicle:
    """Represents a single vehicle with IDM dynamics"""
    id: int
    position: float  # longitudinal position (m)
    speed: float  # speed (m/s)
    lane: int  # lane number (0 = rightmost)
    length: float = 5.0  # vehicle length (m)
    width: float = 2.0  # vehicle width (m)
    v_desired: float = 30.0  # desired speed (m/s) ~108 km/h
    T: float = 1.5  # desired time headway (s)
    s0: float = 2.0  # minimum gap (m)
    a_max: float = 1.0  # maximum acceleration (m/s^2)
    b_comfort: float = 1.5  # comfortable deceleration (m/s^2)
    is_truck: bool = False
    color: str = 'blue'
    
    def __post_init__(self):
        if self.is_truck:
            self.length = 15.0
            self.v_desired = 25.0  # trucks drive slower
            self.color = 'red'


class IDMModel:
    """Intelligent Driver Model for car-following"""
    
    @staticmethod
    def calc_acceleration(veh: Vehicle, leader: Optional[Vehicle], 
                         delta: float = 4.0) -> float:
        """
        Calculate IDM acceleration
        delta: acceleration exponent (typically 4)
        """
        if leader is None:
            # Free road - accelerate to desired speed
            return veh.a_max * (1 - (veh.speed / veh.v_desired) ** delta)
        
        # Calculate gap and approach rate
        s = leader.position - veh.position - leader.length
        dv = veh.speed - leader.speed
        
        # Desired gap
        s_star = veh.s0 + max(0, veh.speed * veh.T + 
                             (veh.speed * dv) / (2 * np.sqrt(veh.a_max * veh.b_comfort)))
        
        # IDM acceleration
        acc = veh.a_max * (1 - (veh.speed / veh.v_desired) ** delta - 
                           (s_star / max(s, 0.1)) ** 2)
        
        return acc


class Road:
    """Represents a road with multiple lanes"""
    
    def __init__(self, length: float, n_lanes: int = 2):
        self.length = length  # road length (m)
        self.n_lanes = n_lanes
        self.vehicles: List[Vehicle] = []
        self.model = IDMModel()
        
    def add_vehicle(self, vehicle: Vehicle):
        """Add a vehicle to the road"""
        self.vehicles.append(vehicle)
        
    def get_leader(self, vehicle: Vehicle) -> Optional[Vehicle]:
        """Find the leader vehicle in the same lane"""
        same_lane = [v for v in self.vehicles 
                     if v.lane == vehicle.lane and v.id != vehicle.id]
        
        # Find vehicles ahead
        ahead = [v for v in same_lane if v.position > vehicle.position]
        
        if not ahead:
            return None
        
        # Return closest vehicle ahead
        return min(ahead, key=lambda v: v.position)
    
    def update(self, dt: float):
        """Update all vehicles for one time step"""
        # Calculate accelerations
        accelerations = {}
        for veh in self.vehicles:
            leader = self.get_leader(veh)
            accelerations[veh.id] = self.model.calc_acceleration(veh, leader)
        
        # Update speeds and positions (ballistic update)
        for veh in self.vehicles:
            acc = accelerations[veh.id]
            veh.speed = max(0, veh.speed + acc * dt)  # speed can't be negative
            veh.position += veh.speed * dt + 0.5 * acc * dt ** 2
            
            # Periodic boundary conditions (ring road)
            if veh.position > self.length:
                veh.position -= self.length
            elif veh.position < 0:
                veh.position += self.length


class TrafficSimulation:
    """Main simulation class with visualization"""
    
    def __init__(self, road_length: float = 1000.0, n_lanes: int = 2):
        self.road = Road(road_length, n_lanes)
        self.dt = 0.1  # time step (s)
        self.time = 0.0
        
        # For visualization
        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(14, 8))
        self.setup_plot()
        
    def setup_plot(self):
        """Setup the visualization"""
        # Top plot: space-time diagram / road view
        self.ax1.set_xlim(0, self.road.length)
        self.ax1.set_ylim(-self.road.n_lanes * 4, 0)
        self.ax1.set_xlabel('Position (m)')
        self.ax1.set_ylabel('Lane')
        self.ax1.set_title('Traffic Simulation (Ring Road)')
        self.ax1.grid(True, alpha=0.3)
        
        # Bottom plot: speed profile
        self.ax2.set_xlim(0, self.road.length)
        self.ax2.set_ylim(0, 40)
        self.ax2.set_xlabel('Position (m)')
        self.ax2.set_ylabel('Speed (m/s)')
        self.ax2.set_title('Speed Profile')
        self.ax2.grid(True, alpha=0.3)
        
    def initialize_traffic(self, n_vehicles: int = 30, truck_fraction: float = 0.2):
        """Initialize vehicles on the road"""
        spacing = self.road.length / n_vehicles
        
        for i in range(n_vehicles):
            is_truck = (i % int(1/truck_fraction) == 0) if truck_fraction > 0 else False
            lane = i % self.road.n_lanes
            
            # Add some randomness to initial speeds
            speed = np.random.uniform(20, 30)
            
            veh = Vehicle(
                id=i,
                position=i * spacing,
                speed=speed,
                lane=lane,
                is_truck=is_truck
            )
            self.road.add_vehicle(veh)
    
    def update_frame(self, frame):
        """Update function for animation"""
        # Update simulation
        self.road.update(self.dt)
        self.time += self.dt
        
        # Clear plots
        self.ax1.clear()
        self.ax2.clear()
        self.setup_plot()
        
        # Draw road lanes
        for lane in range(self.road.n_lanes):
            y = -lane * 4 - 2
            self.ax1.axhline(y=-lane * 4, color='gray', linestyle='--', alpha=0.5)
        
        # Draw vehicles
        for veh in self.road.vehicles:
            y = -veh.lane * 4 - 2
            
            # Vehicle rectangle on road
            rect = Rectangle((veh.position, y - 1), veh.length, 2, 
                           facecolor=veh.color, edgecolor='black', alpha=0.7)
            self.ax1.add_patch(rect)
            
            # Speed plot
            self.ax2.scatter(veh.position, veh.speed, 
                           c=veh.color, s=50, alpha=0.7)
        
        # Add legend
        car_patch = mpatches.Patch(color='blue', label='Car')
        truck_patch = mpatches.Patch(color='red', label='Truck')
        self.ax1.legend(handles=[car_patch, truck_patch], loc='upper right')
        
        self.ax1.set_title(f'Traffic Simulation (Ring Road) - Time: {self.time:.1f}s')
        
        return self.ax1, self.ax2
    
    def run(self, duration: int = 200):
        """Run the simulation"""
        frames = int(duration / self.dt)
        anim = FuncAnimation(self.fig, self.update_frame, 
                           frames=frames, interval=50, blit=False)
        plt.tight_layout()
        plt.show()
        
        return anim


# Example usage
if __name__ == "__main__":
    # Create simulation
    sim = TrafficSimulation(road_length=500, n_lanes=2)
    
    # Initialize with vehicles
    sim.initialize_traffic(n_vehicles=25, truck_fraction=0.15)
    
    # Run simulation
    print("Starting traffic simulation...")
    print("Close the window to end the simulation.")
    anim = sim.run(duration=200)