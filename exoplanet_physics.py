"""
Exoplanet Physics Calculations
Implements physics-based feature engineering for exoplanet detection
"""

import numpy as np
import pandas as pd

class ExoplanetPhysics:
    """Calculate physics-based features for exoplanet analysis"""
    
    # Physical constants
    G = 6.67430e-11  # Gravitational constant (m^3 kg^-1 s^-2)
    R_SUN = 6.957e8  # Solar radius (m)
    M_SUN = 1.989e30  # Solar mass (kg)
    R_EARTH = 6.371e6  # Earth radius (m)
    AU = 1.496e11  # Astronomical unit (m)
    STEFAN_BOLTZMANN = 5.670374419e-8  # Stefan-Boltzmann constant (W m^-2 K^-4)
    
    @staticmethod
    def calculate_impact_parameter(transit_duration, orbital_period, stellar_radius, 
                                   transit_depth=None, eccentricity=0.0):
        """
        Calculate impact parameter (b) from transit properties
        
        Impact parameter: distance between planet's center and star's center
        at mid-transit in units of stellar radii
        
        Formula: b = a/R_star * cos(i)
        where a is semi-major axis and i is inclination
        
        Can be approximated from transit duration and depth
        """
        try:
            # Convert to proper units
            P = orbital_period  # days
            T = transit_duration / 24.0  # convert hours to days
            R_star = stellar_radius  # solar radii
            
            # For circular orbit, simplified formula
            # b ≈ sqrt(1 - (T/T_full)^2)
            # where T_full is transit duration for central transit (b=0)
            
            # More accurate calculation using transit geometry
            # Transit duration formula: T = P/π * arcsin(R_star * sqrt((1+k)^2 - b^2) / a)
            # Simplified for small planet: b ≈ sqrt(1 - (π*T*a)/(P*R_star))^2)
            
            # Kepler's third law to get semi-major axis
            a = stellar_radius  # placeholder, will be calculated properly
            
            # Simplified impact parameter estimation
            # b = sqrt(1 - (transit_duration / max_transit_duration)^2)
            
            # Using transit duration ratio
            # For circular orbit: b ≈ 1 - (T*π/(P*2))
            
            if T > 0 and P > 0 and R_star > 0:
                # Normalized transit duration
                duration_factor = (T * np.pi) / (P * 2)
                
                if transit_depth is not None and transit_depth > 0:
                    # Use transit depth to refine calculation
                    # depth ≈ (R_p/R_star)^2
                    R_ratio = np.sqrt(transit_depth / 1e6)  # depth usually in ppm
                    
                    # Impact parameter from geometry
                    # T/P ≈ (R_star/π*a) * sqrt((1+k)^2 - b^2)
                    # Solving for b:
                    term = 1 - (duration_factor ** 2)
                    b = np.sqrt(max(0, term))
                else:
                    # Without depth information, use simplified formula
                    b = 1.0 - duration_factor
                    b = max(0, min(b, 1.5))  # Physical constraint: 0 <= b <= ~1.5
                
                return b
            else:
                return np.nan
                
        except Exception as e:
            return np.nan
    
    @staticmethod
    def calculate_semi_major_axis(orbital_period, stellar_mass):
        """
        Calculate semi-major axis using Kepler's third law
        
        a^3 = (G * M_star * P^2) / (4 * π^2)
        
        Returns: semi-major axis in AU
        """
        try:
            P = orbital_period * 86400  # Convert days to seconds
            M = stellar_mass * ExoplanetPhysics.M_SUN  # Convert solar masses to kg
            
            # Kepler's third law
            a_cubed = (ExoplanetPhysics.G * M * P**2) / (4 * np.pi**2)
            a = a_cubed ** (1/3)
            
            # Convert to AU
            a_au = a / ExoplanetPhysics.AU
            
            return a_au
        except Exception as e:
            return np.nan
    
    @staticmethod
    def calculate_planet_radius(transit_depth, stellar_radius):
        """
        Calculate planet radius from transit depth
        
        Transit depth = (R_p / R_star)^2
        
        Returns: planet radius in Earth radii
        """
        try:
            if transit_depth <= 0 or stellar_radius <= 0:
                return np.nan
            
            # depth is usually in ppm or percentage
            if transit_depth > 1:  # Assume it's in ppm
                depth_fraction = transit_depth / 1e6
            else:
                depth_fraction = transit_depth
            
            # R_p / R_star = sqrt(depth)
            R_ratio = np.sqrt(depth_fraction)
            
            # Convert to Earth radii
            # R_p = R_ratio * R_star * (R_sun / R_earth)
            R_planet = R_ratio * stellar_radius * (ExoplanetPhysics.R_SUN / ExoplanetPhysics.R_EARTH)
            
            return R_planet
        except Exception as e:
            return np.nan
    
    @staticmethod
    def calculate_equilibrium_temperature(stellar_temp, stellar_radius, semi_major_axis, albedo=0.3):
        """
        Calculate planet equilibrium temperature
        
        T_eq = T_star * sqrt(R_star / 2a) * (1 - A)^(1/4)
        
        where A is the Bond albedo
        
        Returns: equilibrium temperature in Kelvin
        """
        try:
            if stellar_temp <= 0 or stellar_radius <= 0 or semi_major_axis <= 0:
                return np.nan
            
            # Convert semi-major axis to solar radii
            a_solar_radii = semi_major_axis * ExoplanetPhysics.AU / ExoplanetPhysics.R_SUN
            
            # Equilibrium temperature formula
            T_eq = stellar_temp * np.sqrt(stellar_radius / (2 * a_solar_radii)) * ((1 - albedo) ** 0.25)
            
            return T_eq
        except Exception as e:
            return np.nan
    
    @staticmethod
    def calculate_insolation_flux(stellar_temp, stellar_radius, semi_major_axis):
        """
        Calculate insolation flux (energy received by planet)
        
        F = σ * T_star^4 * (R_star / a)^2
        
        Returns: flux relative to Earth's insolation
        """
        try:
            if stellar_temp <= 0 or stellar_radius <= 0 or semi_major_axis <= 0:
                return np.nan
            
            # Convert to SI units
            R_star = stellar_radius * ExoplanetPhysics.R_SUN
            a = semi_major_axis * ExoplanetPhysics.AU
            
            # Calculate flux
            flux = ExoplanetPhysics.STEFAN_BOLTZMANN * (stellar_temp ** 4) * (R_star / a) ** 2
            
            # Earth's insolation is about 1361 W/m^2
            earth_insolation = 1361
            flux_relative = flux / earth_insolation
            
            return flux_relative
        except Exception as e:
            return np.nan
    
    @staticmethod
    def calculate_transit_probability(semi_major_axis, stellar_radius, planet_radius=0):
        """
        Calculate geometric transit probability
        
        P_tr ≈ (R_star + R_planet) / a
        
        Returns: probability (0 to 1)
        """
        try:
            # Convert to same units (solar radii)
            a_solar = semi_major_axis * ExoplanetPhysics.AU / ExoplanetPhysics.R_SUN
            R_p_solar = planet_radius * ExoplanetPhysics.R_EARTH / ExoplanetPhysics.R_SUN
            
            prob = (stellar_radius + R_p_solar) / a_solar
            
            return min(prob, 1.0)
        except Exception as e:
            return np.nan
    
    @staticmethod
    def calculate_transit_snr_metric(transit_depth, snr, transit_duration, orbital_period):
        """
        Calculate a combined SNR metric for transit quality
        
        Better transits have: higher SNR, appropriate depth, longer duration relative to period
        """
        try:
            if snr <= 0 or transit_depth <= 0:
                return np.nan
            
            # Normalize depth (assuming ppm)
            if transit_depth > 1:
                depth_normalized = np.log10(transit_depth)
            else:
                depth_normalized = np.log10(transit_depth * 1e6)
            
            # Duration to period ratio
            duration_ratio = transit_duration / (orbital_period * 24)  # both in hours
            
            # Combined metric
            metric = snr * depth_normalized * np.sqrt(duration_ratio)
            
            return metric
        except Exception as e:
            return np.nan
    
    @staticmethod
    def is_potentially_habitable(planet_temp, planet_radius):
        """
        Rough habitability check based on temperature and size
        
        Habitable zone: 200K < T < 350K
        Earth-like size: 0.5 < R < 2.0 R_earth
        """
        try:
            temp_ok = 200 < planet_temp < 350 if not np.isnan(planet_temp) else False
            size_ok = 0.5 < planet_radius < 2.0 if not np.isnan(planet_radius) else False
            
            return 1 if (temp_ok and size_ok) else 0
        except Exception as e:
            return 0
    
    @staticmethod
    def enrich_features(df):
        """
        Add all physics-based features to dataframe
        """
        print("Calculating physics-based features...")
        
        # Calculate impact parameter if not present
        if 'impact_parameter' not in df.columns or df['impact_parameter'].isna().any():
            print("Calculating impact parameters...")
            df['impact_parameter'] = df.apply(
                lambda row: ExoplanetPhysics.calculate_impact_parameter(
                    row.get('transit_duration', np.nan),
                    row.get('orbital_period', np.nan),
                    row.get('stellar_radius', np.nan),
                    row.get('transit_depth', np.nan)
                ), axis=1
            )
        
        # Calculate semi-major axis
        print("Calculating semi-major axes...")
        if 'stellar_mass' in df.columns:
            df['semi_major_axis'] = df.apply(
                lambda row: ExoplanetPhysics.calculate_semi_major_axis(
                    row.get('orbital_period', np.nan),
                    row.get('stellar_mass', 1.0)  # Default to 1 solar mass if missing
                ), axis=1
            )
        else:
            # Use stellar radius as proxy if mass not available
            df['semi_major_axis'] = df.apply(
                lambda row: ExoplanetPhysics.calculate_semi_major_axis(
                    row.get('orbital_period', np.nan),
                    row.get('stellar_radius', 1.0)  # Rough approximation
                ), axis=1
            )
        
        # Calculate planet radius if not present
        if 'planet_radius' not in df.columns or df['planet_radius'].isna().any():
            print("Calculating planet radii...")
            df['planet_radius'] = df.apply(
                lambda row: ExoplanetPhysics.calculate_planet_radius(
                    row.get('transit_depth', np.nan),
                    row.get('stellar_radius', np.nan)
                ), axis=1
            )
        
        # Calculate equilibrium temperature if not present
        if 'planet_temp' not in df.columns or df['planet_temp'].isna().any():
            print("Calculating equilibrium temperatures...")
            df['planet_temp'] = df.apply(
                lambda row: ExoplanetPhysics.calculate_equilibrium_temperature(
                    row.get('stellar_temp', np.nan),
                    row.get('stellar_radius', np.nan),
                    row.get('semi_major_axis', np.nan)
                ), axis=1
            )
        
        # Calculate insolation flux
        print("Calculating insolation fluxes...")
        df['insolation_flux'] = df.apply(
            lambda row: ExoplanetPhysics.calculate_insolation_flux(
                row.get('stellar_temp', np.nan),
                row.get('stellar_radius', np.nan),
                row.get('semi_major_axis', np.nan)
            ), axis=1
        )
        
        # Calculate transit probability
        print("Calculating transit probabilities...")
        df['transit_probability'] = df.apply(
            lambda row: ExoplanetPhysics.calculate_transit_probability(
                row.get('semi_major_axis', np.nan),
                row.get('stellar_radius', np.nan),
                row.get('planet_radius', 0)
            ), axis=1
        )
        
        # Calculate SNR metric
        print("Calculating SNR metrics...")
        if 'snr' in df.columns:
            df['snr_metric'] = df.apply(
                lambda row: ExoplanetPhysics.calculate_transit_snr_metric(
                    row.get('transit_depth', np.nan),
                    row.get('snr', np.nan),
                    row.get('transit_duration', np.nan),
                    row.get('orbital_period', np.nan)
                ), axis=1
            )
        
        # Habitability flag
        print("Checking habitability...")
        df['potentially_habitable'] = df.apply(
            lambda row: ExoplanetPhysics.is_potentially_habitable(
                row.get('planet_temp', np.nan),
                row.get('planet_radius', np.nan)
            ), axis=1
        )
        
        # Additional derived features
        df['log_orbital_period'] = np.log10(df['orbital_period'].clip(lower=0.001))
        df['log_transit_depth'] = np.log10(df['transit_depth'].clip(lower=0.001))
        df['stellar_density'] = df.get('stellar_mass', 1.0) / (df.get('stellar_radius', 1.0) ** 3)
        
        print("Feature engineering complete!")
        return df

if __name__ == "__main__":
    # Test calculations
    print("Testing physics calculations...")
    
    # Example: Earth-like planet around Sun-like star
    b = ExoplanetPhysics.calculate_impact_parameter(
        transit_duration=13.0,  # hours
        orbital_period=365.25,  # days
        stellar_radius=1.0,  # solar radii
        transit_depth=84  # ppm
    )
    print(f"Impact parameter: {b:.3f}")
    
    a = ExoplanetPhysics.calculate_semi_major_axis(
        orbital_period=365.25,  # days
        stellar_mass=1.0  # solar masses
    )
    print(f"Semi-major axis: {a:.3f} AU")
    
    R_p = ExoplanetPhysics.calculate_planet_radius(
        transit_depth=84,  # ppm
        stellar_radius=1.0  # solar radii
    )
    print(f"Planet radius: {R_p:.2f} Earth radii")
    
    T_eq = ExoplanetPhysics.calculate_equilibrium_temperature(
        stellar_temp=5778,  # K
        stellar_radius=1.0,  # solar radii
        semi_major_axis=1.0  # AU
    )
    print(f"Equilibrium temperature: {T_eq:.1f} K")
