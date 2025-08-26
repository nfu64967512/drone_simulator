#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Earth Coordinate System Module
Handles lat/lon to meter coordinate conversions with Earth curvature correction
"""

import math
import logging
from typing import Tuple, Optional
from config.settings import EARTH_RADIUS_KM, METERS_PER_DEGREE_LAT

logger = logging.getLogger(__name__)

class EarthCoordinateSystem:
    """
    Earth coordinate system with improved precision
    Handles conversion between lat/lon and meter coordinates
    """
    
    def __init__(self):
        self.origin_lat: Optional[float] = None
        self.origin_lon: Optional[float] = None
        self._meters_per_degree_lon: Optional[float] = None
        
    def set_origin(self, lat: float, lon: float) -> None:
        """
        Set coordinate origin and calculate longitude conversion factor
        
        Args:
            lat: Latitude of origin point
            lon: Longitude of origin point
        """
        self.origin_lat = lat
        self.origin_lon = lon
        
        # Pre-calculate longitude conversion factor at this latitude
        self._meters_per_degree_lon = METERS_PER_DEGREE_LAT * math.cos(math.radians(lat))
        
        logger.info(f"Coordinate origin set to: {lat:.8f}, {lon:.8f}")
        logger.info(f"Longitude conversion factor: {self._meters_per_degree_lon:.2f} m/degree")
        
    def lat_lon_to_meters(self, lat: float, lon: float) -> Tuple[float, float]:
        """
        Convert lat/lon to meter coordinates with Earth curvature correction
        
        Args:
            lat: Latitude in decimal degrees
            lon: Longitude in decimal degrees
            
        Returns:
            Tuple of (x, y) coordinates in meters (East, North)
        """
        if self.origin_lat is None or self.origin_lon is None:
            logger.warning("Coordinate origin not set, returning (0, 0)")
            return 0.0, 0.0
            
        # Latitude conversion (1 degree ≈ 111.111 km)
        y = (lat - self.origin_lat) * METERS_PER_DEGREE_LAT
        
        # Longitude conversion (with latitude correction)
        x = (lon - self.origin_lon) * self._meters_per_degree_lon
        
        return x, y
    
    def meters_to_lat_lon(self, x: float, y: float) -> Tuple[float, float]:
        """
        Convert meter coordinates to lat/lon
        
        Args:
            x: East distance in meters
            y: North distance in meters
            
        Returns:
            Tuple of (lat, lon) in decimal degrees
        """
        if self.origin_lat is None or self.origin_lon is None:
            logger.warning("Coordinate origin not set, returning (0, 0)")
            return 0.0, 0.0
            
        # Latitude conversion
        lat = self.origin_lat + y / METERS_PER_DEGREE_LAT
        
        # Longitude conversion
        lon = self.origin_lon + x / self._meters_per_degree_lon
        
        return lat, lon
    
    def calculate_distance(self, lat1: float, lon1: float, 
                          lat2: float, lon2: float) -> float:
        """
        Calculate distance between two lat/lon points using Haversine formula
        
        Args:
            lat1, lon1: First point coordinates
            lat2, lon2: Second point coordinates
            
        Returns:
            Distance in meters
        """
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = (math.sin(dlat/2)**2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2)
        
        c = 2 * math.asin(math.sqrt(a))
        
        # Distance in meters
        distance = EARTH_RADIUS_KM * 1000 * c
        
        return distance
    
    def calculate_bearing(self, lat1: float, lon1: float, 
                         lat2: float, lon2: float) -> float:
        """
        Calculate bearing from point 1 to point 2
        
        Args:
            lat1, lon1: Starting point coordinates
            lat2, lon2: Ending point coordinates
            
        Returns:
            Bearing in degrees (0-360, where 0 is North)
        """
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlon = lon2_rad - lon1_rad
        
        y = math.sin(dlon) * math.cos(lat2_rad)
        x = (math.cos(lat1_rad) * math.sin(lat2_rad) - 
             math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon))
        
        bearing_rad = math.atan2(y, x)
        bearing_deg = math.degrees(bearing_rad)
        
        # Normalize to 0-360 degrees
        bearing_normalized = (bearing_deg + 360) % 360
        
        return bearing_normalized
    
    def get_point_at_distance_bearing(self, lat: float, lon: float, 
                                     distance: float, bearing: float) -> Tuple[float, float]:
        """
        Get a point at specified distance and bearing from given point
        
        Args:
            lat, lon: Starting point coordinates
            distance: Distance in meters
            bearing: Bearing in degrees (0 is North)
            
        Returns:
            Tuple of (lat, lon) for the destination point
        """
        # Convert to radians
        lat_rad = math.radians(lat)
        lon_rad = math.radians(lon)
        bearing_rad = math.radians(bearing)
        
        # Angular distance
        angular_distance = distance / (EARTH_RADIUS_KM * 1000)
        
        # Calculate destination point
        lat2_rad = math.asin(
            math.sin(lat_rad) * math.cos(angular_distance) +
            math.cos(lat_rad) * math.sin(angular_distance) * math.cos(bearing_rad)
        )
        
        lon2_rad = lon_rad + math.atan2(
            math.sin(bearing_rad) * math.sin(angular_distance) * math.cos(lat_rad),
            math.cos(angular_distance) - math.sin(lat_rad) * math.sin(lat2_rad)
        )
        
        # Convert back to degrees
        lat2 = math.degrees(lat2_rad)
        lon2 = math.degrees(lon2_rad)
        
        return lat2, lon2
    
    def is_origin_set(self) -> bool:
        """Check if coordinate origin has been set"""
        return self.origin_lat is not None and self.origin_lon is not None
    
    def get_origin(self) -> Tuple[Optional[float], Optional[float]]:
        """Get current origin coordinates"""
        return self.origin_lat, self.origin_lon
    
    def get_conversion_factors(self) -> Tuple[float, Optional[float]]:
        """
        Get coordinate conversion factors
        
        Returns:
            Tuple of (meters_per_degree_lat, meters_per_degree_lon)
        """
        return METERS_PER_DEGREE_LAT, self._meters_per_degree_lon
    
    def validate_coordinates(self, lat: float, lon: float) -> bool:
        """
        Validate lat/lon coordinates
        
        Args:
            lat: Latitude to validate
            lon: Longitude to validate
            
        Returns:
            True if coordinates are valid
        """
        if not (-90 <= lat <= 90):
            logger.error(f"Invalid latitude: {lat} (must be -90 to 90)")
            return False
            
        if not (-180 <= lon <= 180):
            logger.error(f"Invalid longitude: {lon} (must be -180 to 180)")
            return False
            
        return True
    
    def __str__(self) -> str:
        """String representation of coordinate system"""
        if self.is_origin_set():
            return f"EarthCoordinateSystem(origin: {self.origin_lat:.6f}, {self.origin_lon:.6f})"
        else:
            return "EarthCoordinateSystem(origin: not set)"
    
    def __repr__(self) -> str:
        """Detailed representation of coordinate system"""
        return self.__str__()