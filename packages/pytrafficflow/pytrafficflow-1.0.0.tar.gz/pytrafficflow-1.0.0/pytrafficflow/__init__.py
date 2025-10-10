# Core classes
from .core.vehicle import ParticleCar
from .core.velocity import VelocityFunction
from .models.particle import ParticleTrafficModel

# IDM model classes
from .data.synthetic.one_road import Vehicle, IDMModel, Road, TrafficSimulation

__version__ = '1.0.0'
__all__ = [
    'ParticleCar',
    'VelocityFunction', 
    'ParticleTrafficModel',
    'Vehicle',
    'IDMModel',
    'Road',
    'TrafficSimulation'
]