#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Collision Avoidance System with Precise Trajectory Analysis
Enhanced with collision logging for v5.1
"""

import math
import logging
import numpy as np
from typing import Dict, List, Tuple, Optional
from config.settings import SafetyConfig
from core.collision_logger import CollisionLogger

logger = logging.getLogger(__name__)

class CollisionAvoidanceSystem:
    """
    Advanced collision avoidance system with precise trajectory analysis
    Enhanced with collision logging for professional edition
    """
    
    def __init__(self, safety_config: SafetyConfig, collision_logger: CollisionLogger):
        self.config = safety_config
        self.collision_logger = collision_logger
        self.collision_warnings: List[Dict] = []
        self.trajectory_conflicts: List[Dict] = []
        
        logger.info(f"Collision avoidance system initialized with safety distance: {self.config.safety_distance}m")
        
    def analyze_trajectory_conflicts(self, drones_data: Dict) -> List[Dict]:
        """
        Analyze potential conflict points in entire trajectory
        
        Args:
            drones_data: Dictionary containing drone trajectory data
            
        Returns:
            List of conflict dictionaries with timing and avoidance information
        """
        conflicts = []
        drone_ids = sorted(drones_data.keys())  # Lower numbered drones have higher priority
        
        logger.info(f"Analyzing trajectory conflicts for {len(drone_ids)} drones")
        
        for i in range(len(drone_ids)):
            for j in range(i + 1, len(drone_ids)):
                drone1, drone2 = drone_ids[i], drone_ids[j]
                trajectory1 = drones_data[drone1]['trajectory']
                trajectory2 = drones_data[drone2]['trajectory']
                
                if not trajectory1 or not trajectory2:
                    continue
                
                # Analyze minimum distance throughout trajectory
                conflict_points = self._find_trajectory_conflicts(
                    drone1, trajectory1, drone2, trajectory2
                )
                
                for conflict in conflict_points:
                    # Calculate precise wait time
                    wait_time = self._calculate_precise_wait_time(
                        trajectory1, trajectory2, conflict
                    )
                    
                    conflict['wait_time'] = wait_time
                    conflict['priority_drone'] = drone1  # Lower number has priority
                    conflict['waiting_drone'] = drone2   # Higher number waits
                    
                    # Log collision event
                    self.collision_logger.log_collision(conflict)
                    
                conflicts.extend(conflict_points)
                
                logger.info(f"Trajectory analysis: {drone1} vs {drone2} - "
                           f"Found {len(conflict_points)} potential conflicts")
        
        self.trajectory_conflicts = conflicts
        logger.info(f"Total trajectory conflicts found: {len(conflicts)}")
        
        return conflicts
    
    def _find_trajectory_conflicts(self, drone1: str, traj1: List[Dict], 
                                 drone2: str, traj2: List[Dict]) -> List[Dict]:
        """
        Find conflict points between two trajectories
        
        Args:
            drone1, drone2: Drone identifiers
            traj1, traj2: Trajectory data for each drone
            
        Returns:
            List of conflict points with detailed information
        """
        conflicts = []
        
        # Sample entire trajectory at 0.5s intervals
        max_time = max(traj1[-1]['time'], traj2[-1]['time'])
        time_step = 0.5
        
        for t in np.arange(0, max_time, time_step):
            pos1 = self._interpolate_position(traj1, t)
            pos2 = self._interpolate_position(traj2, t)
            
            if pos1 and pos2:
                distance = self._calculate_distance_3d(pos1, pos2)
                
                if distance < self.config.safety_distance:
                    # Find corresponding waypoint indices for conflict point
                    waypoint1_idx = self._find_nearest_waypoint_index(traj1, t)
                    waypoint2_idx = self._find_nearest_waypoint_index(traj2, t)
                    
                    conflict = {
                        'time': t,
                        'distance': distance,
                        'drone1': drone1,
                        'drone2': drone2,
                        'position1': pos1,
                        'position2': pos2,
                        'waypoint1_index': waypoint1_idx,
                        'waypoint2_index': waypoint2_idx,
                        'severity': 'critical' if distance < self.config.critical_distance else 'warning'
                    }
                    
                    conflicts.append(conflict)
                    
                    logger.warning(f"Conflict detected: {drone1}(WP{waypoint1_idx}) vs "
                                 f"{drone2}(WP{waypoint2_idx}) at {t:.1f}s distance {distance:.2f}m")
        
        return conflicts
    
    def _calculate_precise_wait_time(self, traj1: List[Dict], traj2: List[Dict], 
                                   conflict: Dict) -> float:
        """
        Calculate precise wait time - wait for first drone to fly out of safety distance
        
        Args:
            traj1: Priority drone trajectory
            traj2: Waiting drone trajectory
            conflict: Conflict information
            
        Returns:
            Wait time in seconds
        """
        conflict_time = conflict['time']
        conflict_pos2 = conflict['position2']  # Position of waiting drone
        
        # From conflict time, calculate when first drone flies out of safety distance
        safety_buffer = 2.0  # Additional safety margin
        check_interval = 0.1
        
        for t in np.arange(conflict_time, traj1[-1]['time'], check_interval):
            pos1 = self._interpolate_position(traj1, t)
            if pos1:
                distance = self._calculate_distance_3d(pos1, conflict_pos2)
                
                if distance > (self.config.safety_distance + safety_buffer):
                    wait_time = t - conflict_time
                    logger.info(f"Calculated wait time: {wait_time:.1f}s "
                               f"(first drone flies out of safety distance)")
                    return max(wait_time, 3.0)  # Minimum 3 seconds wait
        
        # If first drone doesn't fly out of safety distance before completing mission,
        # wait for mission completion
        completion_wait = traj1[-1]['time'] - conflict_time + 5.0
        logger.info(f"Using mission completion wait time: {completion_wait:.1f}s")
        return max(completion_wait, 5.0)
    
    def _interpolate_position(self, trajectory: List[Dict], time: float) -> Optional[Dict]:
        """
        Interpolate position at specified time in trajectory
        
        Args:
            trajectory: List of trajectory points
            time: Time to interpolate at
            
        Returns:
            Interpolated position dictionary or None
        """
        if not trajectory:
            return None
            
        # Boundary conditions
        if time >= trajectory[-1]['time']:
            return trajectory[-1]
        if time <= trajectory[0]['time']:
            return trajectory[0]
        
        # Linear interpolation
        for i in range(len(trajectory) - 1):
            t1, t2 = trajectory[i]['time'], trajectory[i + 1]['time']
            if t1 <= time <= t2:
                if t2 - t1 == 0:
                    return trajectory[i]
                    
                ratio = (time - t1) / (t2 - t1)
                return {
                    'x': trajectory[i]['x'] + ratio * (trajectory[i + 1]['x'] - trajectory[i]['x']),
                    'y': trajectory[i]['y'] + ratio * (trajectory[i + 1]['y'] - trajectory[i]['y']),
                    'z': trajectory[i]['z'] + ratio * (trajectory[i + 1]['z'] - trajectory[i]['z']),
                    'time': time
                }
        
        return None
    
    def _find_nearest_waypoint_index(self, trajectory: List[Dict], time: float) -> int:
        """
        Find nearest waypoint index for specified time
        
        Args:
            trajectory: Trajectory data
            time: Time to find waypoint for
            
        Returns:
            Waypoint index
        """
        if not trajectory:
            return 0
            
        min_diff = float('inf')
        nearest_idx = 0
        
        for i, point in enumerate(trajectory):
            if 'waypoint_index' in point:  # Only consider real waypoints, not interpolated points
                time_diff = abs(point['time'] - time)
                if time_diff < min_diff:
                    min_diff = time_diff
                    nearest_idx = point.get('waypoint_index', i)
        
        return nearest_idx
    
    def check_collisions(self, positions: Dict[str, Dict], current_time: float) -> Tuple[List[Dict], Dict[str, float]]:
        """
        Check collisions at current time (for real-time display)
        
        Args:
            positions: Current positions of all drones
            current_time: Current simulation time
            
        Returns:
            Tuple of (collision_warnings, new_loiter_commands)
        """
        self.collision_warnings.clear()
        new_loiters = {}
        
        drone_ids = sorted(positions.keys())
        
        for i in range(len(drone_ids)):
            for j in range(i + 1, len(drone_ids)):
                drone1, drone2 = drone_ids[i], drone_ids[j]
                pos1, pos2 = positions[drone1], positions[drone2]
                
                if pos1 and pos2:
                    distance = self._calculate_distance_3d(pos1, pos2)
                    
                    if distance < self.config.safety_distance:
                        warning = {
                            'drone1': drone1,
                            'drone2': drone2,
                            'distance': distance,
                            'time': current_time,
                            'position': ((pos1['x'] + pos2['x'])/2, 
                                       (pos1['y'] + pos2['y'])/2, 
                                       (pos1['z'] + pos2['z'])/2),
                            'severity': 'critical' if distance < self.config.critical_distance else 'warning'
                        }
                        self.collision_warnings.append(warning)
                        
                        # Log real-time collision with position data
                        collision_data = {
                            **warning,
                            'position1': pos1,
                            'position2': pos2,
                            'waypoint1_index': pos1.get('waypoint_index', 0),
                            'waypoint2_index': pos2.get('waypoint_index', 0)
                        }
                        self.collision_logger.log_collision(collision_data)
        
        return self.collision_warnings, new_loiters
    
    def _calculate_distance_3d(self, pos1: Dict, pos2: Dict) -> float:
        """
        Calculate 3D distance between two positions
        
        Args:
            pos1, pos2: Position dictionaries with x, y, z coordinates
            
        Returns:
            3D distance in meters
        """
        return math.sqrt((pos1['x'] - pos2['x'])**2 + 
                        (pos1['y'] - pos2['y'])**2 + 
                        (pos1['z'] - pos2['z'])**2)
    
    def update_safety_config(self, new_config: SafetyConfig) -> None:
        """
        Update safety configuration
        
        Args:
            new_config: New safety configuration
        """
        old_distance = self.config.safety_distance
        self.config = new_config
        
        logger.info(f"Safety configuration updated: distance {old_distance}m → {new_config.safety_distance}m")
    
    def get_collision_summary(self) -> Dict:
        """
        Get summary of collision detection status
        
        Returns:
            Dictionary with collision summary information
        """
        trajectory_conflicts = len(self.trajectory_conflicts)
        current_warnings = len(self.collision_warnings)
        total_logged = len(self.collision_logger)
        
        return {
            'trajectory_conflicts': trajectory_conflicts,
            'current_warnings': current_warnings,
            'total_logged_events': total_logged,
            'safety_distance': self.config.safety_distance,
            'critical_distance': self.config.critical_distance,
            'check_interval': self.config.collision_check_interval
        }
    
    def clear_warnings(self) -> int:
        """
        Clear current collision warnings
        
        Returns:
            Number of warnings cleared
        """
        count = len(self.collision_warnings)
        self.collision_warnings.clear()
        logger.info(f"Cleared {count} collision warnings")
        return count
    
    def __str__(self) -> str:
        """String representation of collision avoidance system"""
        summary = self.get_collision_summary()
        return (f"CollisionAvoidanceSystem(safety: {summary['safety_distance']}m, "
                f"conflicts: {summary['trajectory_conflicts']}, "
                f"warnings: {summary['current_warnings']})")