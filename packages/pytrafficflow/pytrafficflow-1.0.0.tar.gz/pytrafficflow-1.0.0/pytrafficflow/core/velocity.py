"""
Velocity function implementation for traffic flow models
Implements non-linear velocity functions from Equation 4
"""

import numpy as np


class VelocityFunction:
    """
    Non-linear velocity function v(ρ) with three regions:
    1. v = vmax for ρ ≤ ρc
    2. v = K1(ρ^(-K2) - ρmax^(-K2))^K3 for ρc < ρ < ρmax
    3. v = 0 for ρ ≥ ρmax
    """
    
    def __init__(self, vmax, dmin, lcar, K1, K2, rho_c=None):
        """
        Parameters:
        -----------
        vmax : float
            Maximum speed (km/h)
        dmin : float
            Minimum distance between cars (km)
        lcar : float
            Length of a car (km)
        K1, K2 : float
            Shape parameters for velocity curve
        rho_c : float, optional
            Critical density where velocity starts decreasing
        """
        self.vmax = vmax
        self.dmin = dmin
        self.lcar = lcar
        self.K1 = K1
        self.K2 = K2
        
        # Calculate rho_max from Equation 2
        self.rho_max = lcar / (lcar + dmin)
        
        # Set or calculate rho_c
        if rho_c is not None:
            self.rho_c = rho_c
        else:
            self.rho_c = 0.175  # default value
        
        # Calculate K3 from Equation 5 for continuity
        self.K3 = np.log(vmax / K1) / np.log(self.rho_c**(-K2) - self.rho_max**(-K2))
    
    def __call__(self, rho):
        """
        Evaluate velocity function at density rho
        
        Parameters:
        -----------
        rho : array-like
            Car density (0 to 1)
            
        Returns:
        --------
        v : array-like
            Velocity at each density point (km/h)
        """
        rho = np.asarray(rho)
        v = np.zeros_like(rho, dtype=float)
        
        # Region 1: rho <= rho_c (free flow)
        mask1 = rho <= self.rho_c
        v[mask1] = self.vmax
        
        # Region 2: rho_c < rho < rho_max (congested)
        mask2 = (rho > self.rho_c) & (rho < self.rho_max)
        if np.any(mask2):
            v[mask2] = self.K1 * (rho[mask2]**(-self.K2) - self.rho_max**(-self.K2))**self.K3
        
        # Region 3: rho >= rho_max (stopped)
        v[rho >= self.rho_max] = 0
        
        return v
    
    def derivative(self, rho):
        """
        Compute derivative dv/dρ for characteristic speeds
        
        Parameters:
        -----------
        rho : array-like
            Car density
            
        Returns:
        --------
        dv_drho : array-like
            Derivative of velocity with respect to density
        """
        rho = np.asarray(rho)
        dv = np.zeros_like(rho, dtype=float)
        
        # Only non-zero in region 2
        mask = (rho > self.rho_c) & (rho < self.rho_max)
        if np.any(mask):
            base = rho[mask]**(-self.K2) - self.rho_max**(-self.K2)
            dv[mask] = self.K1 * self.K3 * base**(self.K3 - 1) * \
                       (-self.K2) * rho[mask]**(-self.K2 - 1)
        
        return dv
    
    def flux(self, rho):
        """
        Compute flux f(ρ) = v(ρ) * ρ
        
        Parameters:
        -----------
        rho : array-like
            Car density
            
        Returns:
        --------
        f : array-like
            Traffic flux (cars per hour)
        """
        return self(rho) * rho
    
    def flux_derivative(self, rho):
        """
        Compute f'(ρ) = v(ρ) + ρ * v'(ρ)
        
        Parameters:
        -----------
        rho : array-like
            Car density
            
        Returns:
        --------
        df_drho : array-like
            Derivative of flux
        """
        return self(rho) + rho * self.derivative(rho)