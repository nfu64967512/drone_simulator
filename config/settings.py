#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration classes and global constants for v5.1
Enhanced with 6m spacing and professional settings
"""

from dataclasses import dataclass

# Earth coordinate constants
EARTH_RADIUS_KM = 6371.0
METERS_PER_DEGREE_LAT = 111111.0

@dataclass
class SafetyConfig:
    """Safety configuration with enhanced parameters"""
    safety_distance: float = 5.0
    warning_distance: float = 8.0
    critical_distance: float = 3.0
    collision_check_interval: float = 0.1

@dataclass
class TakeoffConfig:
    """Takeoff configuration - Updated to 6m spacing for v5.1"""
    formation_spacing: float = 6.0  # Enhanced from 3.0 to 6.0 meters
    takeoff_altitude: float = 10.0
    hover_time: float = 2.0
    east_offset: float = 50.0

class FlightPhase:
    """Flight phases enumeration"""
    TAXI = "taxi"
    TAKEOFF = "takeoff"
    HOVER = "hover"
    AUTO = "auto"
    LOITER = "loiter"
    LANDING = "landing"

class SimulatorConfig:
    """Simulator configuration constants"""
    # Version info
    VERSION = "5.1.0"
    EDITION = "Professional Edition"
    
    # Performance optimization
    UPDATE_INTERVAL = 33  # ~30fps
    MAX_DRONES = 4
    
    # UI configuration
    WINDOW_TITLE = "Advanced Drone Swarm Simulator - Professional Edition v5.1"
    WINDOW_SIZE = "1920x1080"
    
    # Color configuration for drones
    DRONE_COLORS = ['#FF4444', '#44FF44', '#4444FF', '#FFFF44']
    
    # 3D plot configuration
    FIGURE_SIZE = (18, 12)
    DPI = 100
    
    # Animation configuration
    DEFAULT_CRUISE_SPEED = 8.0  # m/s
    TIME_SCALE_RANGE = (0.1, 5.0)
    SAFETY_DISTANCE_RANGE = (2.0, 15.0)
    
    # File export settings
    COLLISION_LOG_PREFIX = "collision_log"
    MISSION_FILE_PREFIX = "modified"
    EXPORT_ENCODING = "utf-8"
    
    # UI Colors (Dark theme)
    UI_COLORS = {
        'background': '#1e1e1e',
        'panel': '#2d2d2d',
        'accent': '#00d4aa',
        'text': '#ffffff',
        'success': '#4caf50',
        'warning': '#ffc107',
        'danger': '#f44336',
        'info': '#17a2b8'
    }
    
    # Button configurations
    BUTTON_CONFIGS = {
        'play': {'bg': '#28a745', 'fg': 'white'},
        'pause': {'bg': '#ffc107', 'fg': 'black'},
        'stop': {'bg': '#dc3545', 'fg': 'white'},
        'reset': {'bg': '#ffc107', 'fg': 'black'},
        'export': {'bg': '#17a2b8', 'fg': 'white'},
        'log': {'bg': '#e83e8c', 'fg': 'white'}
    }

class CollisionLogConfig:
    """Collision logging configuration"""
    # Log file settings
    FILE_EXTENSION = ".json"
    TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"
    
    # JSON export settings
    INDENT = 2
    ENSURE_ASCII = False
    
    # Metadata fields
    METADATA_FIELDS = [
        'total_events',
        'export_time', 
        'simulation_version'
    ]
    
    # Event data fields
    EVENT_FIELDS = [
        'timestamp',
        'simulation_time',
        'drone1',
        'drone2', 
        'distance',
        'severity',
        'position1',
        'position2',
        'waypoint1_index',
        'waypoint2_index'
    ]

class UILabels:
    """UI labels in English for professional edition"""
    
    # Main sections
    DRONE_SIMULATOR = "🚁 Drone Swarm Simulator"
    MISSION_FILES = "📁 Mission Files"
    DRONE_STATUS = "🎨 Drones"
    CONTROLS = "▶️ Controls"
    STATUS_INFO = "📊 Status Info"
    COLLISION_ALERTS = "⚠️ Collision Alerts"
    
    # Buttons
    PLAY = "▶"
    PAUSE = "⏸"
    STOP = "⏹"
    RESET = "↻"
    EXPORT_MISSIONS = "💾"
    EXPORT_LOG = "📊"
    
    # File operations
    LOAD_QGC = "QGC"
    LOAD_CSV = "CSV"
    CREATE_TEST = "Test"
    
    # View controls
    TOP_VIEW = "Top View"
    SIDE_VIEW = "Side View"
    VIEW_3D = "3D View"
    
    # Status messages
    STANDBY = "Standby"
    READY = "Ready"
    LOADING = "Loading"
    ERROR = "Error"
    
    # Flight phases (display names)
    PHASE_NAMES = {
        FlightPhase.TAXI: "Ground Taxi",
        FlightPhase.TAKEOFF: "Taking Off",
        FlightPhase.HOVER: "Hover Wait",
        FlightPhase.AUTO: "Auto Mission",
        FlightPhase.LOITER: "Avoidance Wait",
        FlightPhase.LANDING: "Landing"
    }
    
    # Menu items
    MENU_FILE = "File"
    MENU_VIEW = "View"
    MENU_SIMULATION = "Simulation"
    MENU_HELP = "Help"
    
    # Dialog messages
    MISSION_CREATED = "Mission Created"
    LOAD_SUCCESS = "Load Success"
    EXPORT_SUCCESS = "Export Success"
    EXPORT_INFO = "Export Info"
    
class AxisLabels:
    """3D plot axis labels in English"""
    X_AXIS = "East Distance (m)"
    Y_AXIS = "North Distance (m)"
    Z_AXIS = "Flight Altitude (m)"
    TITLE = "Drone Swarm 3D Trajectory Simulation - Professional Edition"