#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Drone Simulator - Main Simulator Class for v5.1
Integrates all modules into a comprehensive drone swarm simulation system
"""

import time
import math
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from tkinter import messagebox, filedialog

# Import configuration
from config.settings import (
    SafetyConfig, TakeoffConfig, FlightPhase, SimulatorConfig, UILabels
)

# Import core modules
from core.coordinate_system import EarthCoordinateSystem
from core.collision_logger import CollisionLogger
from core.collision_avoidance import CollisionAvoidanceSystem
from core.flight_manager import TakeoffManager, QGCWaypointGenerator

# Import GUI modules
from gui.main_window import MainWindow
from gui.control_panel import ControlPanel
from gui.plot_manager import Plot3DManager

# Import simulator modules
from simulator.file_parser import FileParserFactory

# Import utilities
from utils.logging_config import setup_logging, log_performance

logger = logging.getLogger(__name__)

class AdvancedDroneSimulator:
    """
    Advanced Drone Swarm Simulator v5.1 - Professional Edition
    
    Main simulator class that integrates all modules to provide:
    - Real-time collision detection and avoidance
    - 2x2 formation takeoff with 6m spacing
    - Professional 3D visualization
    - QGC waypoint file generation
    - Comprehensive collision logging
    - English professional interface
    """
    
    def __init__(self):
        """Initialize the advanced drone simulator"""
        logger.info("🚁 Initializing Advanced Drone Simulator v5.1")
        
        # Core systems
        self.coordinate_system = EarthCoordinateSystem()
        self.safety_config = SafetyConfig()
        self.takeoff_config = TakeoffConfig()
        self.collision_logger = CollisionLogger()
        self.collision_system = CollisionAvoidanceSystem(self.safety_config, self.collision_logger)
        self.takeoff_manager = TakeoffManager(self.takeoff_config, self.coordinate_system)
        self.qgc_generator = QGCWaypointGenerator()
        
        # Simulation data
        self.drones: Dict[str, Dict] = {}
        self.current_time = 0.0
        self.max_time = 0.0
        self.time_scale = 1.0
        self.is_playing = False
        self.modified_missions: Dict[str, List[str]] = {}
        
        # Performance optimization
        self.last_collision_check = 0.0
        self.update_interval = SimulatorConfig.UPDATE_INTERVAL
        self.last_update_time = time.time()
        
        # GUI components
        self.main_window: Optional[MainWindow] = None
        self.control_panel: Optional[ControlPanel] = None
        self.plot_manager: Optional[Plot3DManager] = None
        
        # Animation
        self.animation = None
        
        # Initialize collision logger
        self.collision_logger.initialize_log_file("drone_simulator_collisions")
        
        logger.info("✅ Advanced Drone Simulator initialized successfully")
    
    def run(self) -> None:
        """
        Run the complete simulator application
        """
        logger.info("🚀 Starting Advanced Drone Simulator")
        
        try:
            # Setup GUI
            self._setup_gui()
            
            # Register callbacks
            self._register_callbacks()
            
            # Initialize display
            self._update_status_display()
            self._update_3d_plot()
            
            # Log system information
            from utils.logging_config import log_system_info
            log_system_info()
            
            logger.info("🎯 Simulator ready - GUI started")
            
            # Run main loop
            self.main_window.get_window().mainloop()
            
        except Exception as e:
            logger.error(f"💥 Fatal error in simulator: {e}")
            if self.main_window:
                self.main_window.show_error("Fatal Error", f"Simulator encountered a fatal error:\n{e}")
            raise
        finally:
            self._cleanup()
    
    def _setup_gui(self) -> None:
        """Setup the complete GUI system"""
        logger.info("🖥️ Setting up GUI components")
        
        # Create main window
        self.main_window = MainWindow()
        window = self.main_window.create_window()
        
        # Create main container
        main_container = window
        
        # Create control panel
        self.control_panel = ControlPanel(main_container)
        control_frame = self.control_panel.create_panel()
        
        # Create 3D plot manager
        plot_container_frame = main_container
        self.plot_manager = Plot3DManager(plot_container_frame)
        plot_frame = self.plot_manager.setup_plot()
        
        # Create menu and shortcuts
        self.main_window.create_menu()
        self.main_window.bind_shortcuts()
        
        logger.info("✅ GUI setup completed")
    
    def _register_callbacks(self) -> None:
        """Register all callback functions"""
        logger.info("🔗 Registering callbacks")
        
        # Main window callbacks
        main_callbacks = {
            'load_qgc_files': self.load_qgc_files,
            'load_csv_files': self.load_csv_files,
            'create_test_mission': self.create_test_mission,
            'export_modified_missions': self.export_modified_missions,
            'export_collision_log': self.export_collision_log,
            'toggle_play': self.toggle_play,
            'stop_simulation': self.stop_simulation,
            'reset_simulation': self.reset_simulation,
            'set_top_view': self.set_top_view,
            'set_side_view': self.set_side_view,
            'set_3d_view': self.set_3d_view,
            'analyze_collisions': self.analyze_collisions,
            'clear_warnings': self.clear_warnings,
            'on_closing': self.on_closing
        }
        
        for event, callback in main_callbacks.items():
            self.main_window.register_callback(event, callback)
        
        # Control panel callbacks
        control_callbacks = {
            'load_qgc_files': self.load_qgc_files,
            'load_csv_files': self.load_csv_files,
            'create_test_mission': self.create_test_mission,
            'toggle_play': self.toggle_play,
            'stop_simulation': self.stop_simulation,
            'reset_simulation': self.reset_simulation,
            'export_modified_missions': self.export_modified_missions,
            'export_collision_log': self.export_collision_log,
            'on_time_change': self.on_time_change,
            'on_speed_change': self.on_speed_change,
            'on_safety_change': self.on_safety_change
        }
        
        for event, callback in control_callbacks.items():
            self.control_panel.register_callback(event, callback)
        
        logger.debug("📝 All callbacks registered successfully")
    
    @log_performance
    def create_test_mission(self) -> None:
        """Create comprehensive test mission with 2x2 formation"""
        logger.info("🧪 Creating test mission with 2x2 formation")
        
        try:
            self.drones.clear()
            self.modified_missions.clear()
            
            # Set base coordinates (Taiwan area for testing)
            base_lat, base_lon = 24.0, 121.0
            self.coordinate_system.set_origin(base_lat, base_lon)
            
            # Generate 2x2 takeoff formation with 6m spacing
            takeoff_positions = self.takeoff_manager.generate_takeoff_formation(base_lat, base_lon)
            
            # Create mission for each drone
            for i in range(4):
                drone_id = f"Drone_{i+1}"
                takeoff_lat, takeoff_lon = takeoff_positions[i]
                
                # Create waypoints
                waypoints = self._generate_test_waypoints(i, takeoff_lat, takeoff_lon, base_lat, base_lon)
                
                # Calculate trajectory
                trajectory = self._calculate_realistic_trajectory(waypoints, drone_id)
                
                # Store drone data
                self.drones[drone_id] = {
                    'waypoints': waypoints,
                    'trajectory': trajectory,
                    'color': SimulatorConfig.DRONE_COLORS[i],
                    'takeoff_position': (takeoff_lat, takeoff_lon),
                    'phase': FlightPhase.TAXI,
                    'loiter_delays': [],
                    'current_position': None
                }
                
                # Update status
                self.control_panel.update_drone_status(f'drone_{i+1}', '✓ Ready', '#4caf50')
                
                logger.debug(f"Created test mission for {drone_id}")
            
            # Update simulation
            self._calculate_max_time()
            self._update_status_display()
            self._update_3d_plot()
            
            self.main_window.show_info(
                UILabels.MISSION_CREATED,
                f"Created 2x2 east takeoff formation test mission\n"
                f"• Formation spacing: {self.takeoff_config.formation_spacing}m\n"
                f"• Safety distance: {self.safety_config.safety_distance}m\n"
                f"• {len(self.drones)} drones ready for simulation"
            )
            
            logger.info("✅ Test mission created successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to create test mission: {e}")
            self.main_window.show_error("Mission Creation Failed", f"Failed to create test mission:\n{e}")
    
    def _generate_test_waypoints(self, drone_index: int, takeoff_lat: float, takeoff_lon: float,
                                base_lat: float, base_lon: float) -> List[Dict]:
        """Generate test waypoints for a specific drone"""
        waypoints = []
        
        # HOME point
        waypoints.append({
            'lat': takeoff_lat,
            'lon': takeoff_lon,
            'alt': 0,
            'cmd': 179  # HOME
        })
        
        # Mission area assignment (different regions to test collision scenarios)
        region_offsets = [
            (-100, -50),  # Southwest - Drone_1
            (100, -50),   # Southeast - Drone_2  
            (-100, 50),   # Northwest - Drone_3
            (100, 50)     # Northeast - Drone_4
        ]
        
        offset_x, offset_y = region_offsets[drone_index]
        base_x, base_y = self.coordinate_system.lat_lon_to_meters(base_lat, base_lon)
        
        # Generate rectangular mission pattern
        mission_points = [
            (base_x + offset_x, base_y + offset_y, 15),
            (base_x + offset_x + 80, base_y + offset_y, 15),
            (base_x + offset_x + 80, base_y + offset_y + 80, 15),
            (base_x + offset_x, base_y + offset_y + 80, 15),
            (base_x + offset_x, base_y + offset_y, 15)
        ]
        
        # Convert to lat/lon and add to waypoints
        for mx, my, mz in mission_points:
            mlat, mlon = self.coordinate_system.meters_to_lat_lon(mx, my)
            waypoints.append({
                'lat': mlat,
                'lon': mlon,
                'alt': mz,
                'cmd': 16
            })
        
        return waypoints
    
    @log_performance
    def _calculate_realistic_trajectory(self, waypoints: List[Dict], drone_id: str) -> List[Dict]:
        """Calculate realistic trajectory with proper timing and phases"""
        trajectory = []
        total_time = 0.0
        speed = SimulatorConfig.DEFAULT_CRUISE_SPEED
        
        if len(waypoints) < 2:
            return trajectory
        
        # Phase 1: Ground taxi (0-2s)
        home_wp = waypoints[0]
        home_x, home_y = self.coordinate_system.lat_lon_to_meters(home_wp['lat'], home_wp['lon'])
        
        trajectory.append({
            'x': home_x, 'y': home_y, 'z': 0,
            'time': 0.0, 'phase': FlightPhase.TAXI,
            'lat': home_wp['lat'], 'lon': home_wp['lon'], 'alt': 0,
            'waypoint_index': 0
        })
        
        # Phase 2: Takeoff (2-7s)
        takeoff_time = 2.0
        climb_duration = 5.0
        
        for i, t in enumerate(np.linspace(takeoff_time, takeoff_time + climb_duration, 20)):
            progress = (t - takeoff_time) / climb_duration
            altitude = progress * self.takeoff_config.takeoff_altitude
            
            trajectory.append({
                'x': home_x, 'y': home_y, 'z': altitude,
                'time': t, 'phase': FlightPhase.TAKEOFF,
                'lat': home_wp['lat'], 'lon': home_wp['lon'], 'alt': altitude,
                'waypoint_index': 0 if i < 10 else 1
            })
        
        total_time = takeoff_time + climb_duration
        
        # Phase 3: Hover wait (7-9s)
        hover_end_time = total_time + self.takeoff_config.hover_time
        
        trajectory.append({
            'x': home_x, 'y': home_y, 'z': self.takeoff_config.takeoff_altitude,
            'time': hover_end_time, 'phase': FlightPhase.HOVER,
            'lat': home_wp['lat'], 'lon': home_wp['lon'], 'alt': self.takeoff_config.takeoff_altitude,
            'waypoint_index': 1
        })
        
        total_time = hover_end_time
        
        # Phase 4: Auto mission
        prev_x, prev_y, prev_z = home_x, home_y, self.takeoff_config.takeoff_altitude
        
        for wp_idx, wp in enumerate(waypoints[1:], start=2):
            x, y = self.coordinate_system.lat_lon_to_meters(wp['lat'], wp['lon'])
            z = wp['alt']
            
            # Calculate flight time
            distance = math.sqrt((x - prev_x)**2 + (y - prev_y)**2 + (z - prev_z)**2)
            flight_time = distance / speed
            total_time += flight_time
            
            # Add interpolation points for smooth trajectory
            if distance > 10:
                num_segments = max(2, int(distance / 10))
                for seg in range(1, num_segments):
                    ratio = seg / num_segments
                    interp_time = total_time - flight_time + (flight_time * ratio)
                    interp_x = prev_x + ratio * (x - prev_x)
                    interp_y = prev_y + ratio * (y - prev_y)
                    interp_z = prev_z + ratio * (z - prev_z)
                    
                    trajectory.append({
                        'x': interp_x, 'y': interp_y, 'z': interp_z,
                        'time': interp_time, 'phase': FlightPhase.AUTO,
                        'lat': wp['lat'], 'lon': wp['lon'], 'alt': wp['alt'],
                        'waypoint_index': wp_idx - 1
                    })
            
            # Add actual waypoint
            trajectory.append({
                'x': x, 'y': y, 'z': z,
                'time': total_time, 'phase': FlightPhase.AUTO,
                'lat': wp['lat'], 'lon': wp['lon'], 'alt': wp['alt'],
                'waypoint_index': wp_idx
            })
            
            prev_x, prev_y, prev_z = x, y, z
        
        logger.debug(f"Calculated trajectory for {drone_id}: {len(trajectory)} points, {total_time:.1f}s")
        return trajectory
    
    def load_qgc_files(self) -> None:
        """Load QGC waypoint files"""
        logger.info("📁 Loading QGC files")
        
        file_paths = filedialog.askopenfilenames(
            title="Select QGC Waypoint Files",
            filetypes=[("Waypoint files", "*.waypoints"), ("All files", "*.*")]
        )
        
        if file_paths:
            self._load_mission_files(file_paths, "QGC")
    
    def load_csv_files(self) -> None:
        """Load CSV waypoint files"""
        logger.info("📁 Loading CSV files")
        
        file_paths = filedialog.askopenfilenames(
            title="Select CSV Waypoint Files",
            filetypes=[("CSV files", "*.csv"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_paths:
            self._load_mission_files(file_paths, "CSV")
    
    @log_performance
    def _load_mission_files(self, file_paths: List[str], file_type: str) -> None:
        """Load mission files with comprehensive error handling"""
        logger.info(f"📂 Loading {len(file_paths)} {file_type} files")
        
        self.drones.clear()
        self.modified_missions.clear()
        
        # Reset drone status
        for i in range(4):
            self.control_panel.update_drone_status(f'drone_{i+1}', UILabels.LOADING, '#888')
        
        loaded_count = 0
        
        for i, file_path in enumerate(file_paths):
            if i >= SimulatorConfig.MAX_DRONES:
                logger.warning(f"Maximum {SimulatorConfig.MAX_DRONES} drones supported, ignoring additional files")
                break
            
            try:
                drone_id = f"Drone_{i+1}"
                
                # Parse file using factory
                waypoints = FileParserFactory.parse_mission_file(file_path)
                
                if waypoints:
                    # Set coordinate origin from first file
                    if i == 0:
                        self.coordinate_system.set_origin(waypoints[0]['lat'], waypoints[0]['lon'])
                    
                    # Calculate trajectory
                    trajectory = self._calculate_realistic_trajectory(waypoints, drone_id)
                    
                    # Store drone data
                    self.drones[drone_id] = {
                        'waypoints': waypoints,
                        'trajectory': trajectory,
                        'color': SimulatorConfig.DRONE_COLORS[i],
                        'takeoff_position': (waypoints[0]['lat'], waypoints[0]['lon']),
                        'phase': FlightPhase.TAXI,
                        'loiter_delays': [],
                        'file_path': file_path,
                        'current_position': None
                    }
                    
                    # Update status
                    self.control_panel.update_drone_status(f'drone_{i+1}', f'✓ {drone_id}', '#4caf50')
                    
                    loaded_count += 1
                    logger.info(f"✅ Loaded {drone_id}: {len(waypoints)} waypoints from {file_path}")
                else:
                    raise ValueError("No valid waypoints found")
                    
            except Exception as e:
                logger.error(f"❌ Failed to load {file_path}: {e}")
                self.control_panel.update_drone_status(f'drone_{i+1}', '✗ Error', '#f44336')
        
        if loaded_count > 0:
            self._calculate_max_time()
            self._update_status_display()
            self._update_3d_plot()
            
            self.main_window.show_info(
                UILabels.LOAD_SUCCESS,
                f"Successfully loaded {loaded_count} drone missions\n"
                f"File type: {file_type}\n"
                f"Ready for simulation"
            )
        else:
            self.main_window.show_warning(
                "Load Warning",
                "No valid drone missions were loaded.\n"
                "Please check file formats and try again."
            )
    
    def toggle_play(self) -> None:
        """Toggle play/pause simulation"""
        self.is_playing = not self.is_playing
        
        if self.is_playing:
            logger.info("▶️ Starting simulation")
            self.control_panel.update_play_button(True)
            self._start_animation()
        else:
            logger.info("⏸️ Pausing simulation")
            self.control_panel.update_play_button(False)
            self._stop_animation()
    
    def stop_simulation(self) -> None:
        """Stop simulation"""
        logger.info("⏹️ Stopping simulation")
        self.is_playing = False
        self.control_panel.update_play_button(False)
        self._stop_animation()
    
    def reset_simulation(self) -> None:
        """Reset simulation to beginning"""
        logger.info("↻ Resetting simulation")
        
        self.stop_simulation()
        self.current_time = 0.0
        self.control_panel.set_variable_value('time_var', 0.0)
        self.last_collision_check = 0.0
        
        # Clear delays and warnings
        for drone_data in self.drones.values():
            drone_data['loiter_delays'] = []
        
        self.modified_missions.clear()
        self.collision_logger.clear_events()
        
        # Update displays
        self._update_status_display()
        self._update_3d_plot()
        
        logger.info("✅ Simulation reset completed")
    
    def _start_animation(self) -> None:
        """Start high-performance animation loop"""
        if self.animation:
            self.animation.event_source.stop()
        
        self.last_update_time = time.time()
        
        def update_frame(frame):
            if not self.is_playing or self.max_time == 0:
                return
            
            current_real_time = time.time()
            dt = (current_real_time - self.last_update_time) * self.time_scale
            self.last_update_time = current_real_time
            
            self.current_time += dt
            
            if self.current_time > self.max_time:
                self.current_time = self.max_time
                self.toggle_play()
                return
            
            # Update UI (reduced frequency for performance)
            if frame % 2 == 0:
                self.control_panel.set_variable_value('time_var', self.current_time)
                self.control_panel.update_time_display(self.current_time, self.max_time)
                self._update_status_display()
            
            # Update 3D plot
            self._update_3d_plot()
        
        # Import animation here to avoid circular imports
        import matplotlib.animation as animation
        self.animation = animation.FuncAnimation(
            self.plot_manager.fig, update_frame, 
            interval=self.update_interval, blit=False
        )
    
    def _stop_animation(self) -> None:
        """Stop animation"""
        if self.animation:
            self.animation.event_source.stop()
            self.animation = None
    
    @log_performance
    def _update_3d_plot(self) -> None:
        """Update 3D visualization"""
        if not self.plot_manager:
            return
        
        # Get current positions
        current_positions = self._get_current_positions()
        
        # Collision detection (throttled for performance)
        warnings = []
        if self.current_time - self.last_collision_check >= self.safety_config.collision_check_interval:
            warnings, new_loiters = self.collision_system.check_collisions(current_positions, self.current_time)
            
            # Apply new LOITER delays
            for drone_id, loiter_time in new_loiters.items():
                if drone_id in self.drones:
                    self.drones[drone_id]['loiter_delays'].append({
                        'start_time': self.current_time,
                        'duration': loiter_time
                    })
            
            self.last_collision_check = self.current_time
            
            # Update warning display
            self._update_warning_display(warnings)
            
            # Generate modified missions if needed
            if warnings and not self.modified_missions:
                self._generate_modified_missions(new_loiters)
        
        # Update 3D plot
        self.plot_manager.update_plot(
            self.drones,
            warnings,
            self.current_time,
            self.safety_config.safety_distance
        )
    
    def _get_current_positions(self) -> Dict[str, Dict]:
        """Get current positions of all drones"""
        positions = {}
        
        for drone_id, drone_data in self.drones.items():
            trajectory = drone_data['trajectory']
            if trajectory:
                position = self._get_drone_position_at_time(drone_id, self.current_time)
                if position:
                    positions[drone_id] = position
        
        return positions
    
    def _get_drone_position_at_time(self, drone_id: str, time: float) -> Optional[Dict]:
        """Get drone position at specific time with LOITER delays"""
        if drone_id not in self.drones:
            return None
        
        trajectory = self.drones[drone_id]['trajectory']
        if not trajectory:
            return None
        
        # Apply LOITER delays
        effective_time = time
        for delay in self.drones[drone_id].get('loiter_delays', []):
            if time >= delay['start_time']:
                effective_time = max(delay['start_time'], time - delay['duration'])
                break
        
        # Interpolate position
        return self.collision_system._interpolate_position(trajectory, effective_time)
    
    def _calculate_max_time(self) -> None:
        """Calculate maximum simulation time"""
        self.max_time = 0.0
        
        for drone_data in self.drones.values():
            trajectory = drone_data['trajectory']
            if trajectory:
                base_time = trajectory[-1]['time']
                total_loiter = sum(delay['duration'] for delay in drone_data.get('loiter_delays', []))
                drone_max_time = base_time + total_loiter
                self.max_time = max(self.max_time, drone_max_time)
        
        if self.max_time > 0:
            self.control_panel.get_widget('time_slider').config(to=self.max_time)
        
        logger.debug(f"Maximum simulation time: {self.max_time:.1f}s")
    
    def _update_status_display(self) -> None:
        """Update status text display"""
        if not self.control_panel:
            return
        
        if not self.drones:
            self.control_panel.update_status_text("📄 No loaded drones\n\nLoad mission files or create test mission to begin.")
            return
        
        status_lines = []
        
        for drone_id, drone_data in self.drones.items():
            trajectory = drone_data['trajectory']
            current_pos = self._get_drone_position_at_time(drone_id, self.current_time)
            
            status_lines.append(f"🚁 {drone_id}:")
            status_lines.append(f"   📍 Takeoff: {drone_data['takeoff_position']}")
            status_lines.append(f"   📊 Waypoints: {len(drone_data['waypoints'])}")
            
            if trajectory:
                status_lines.append(f"   ⏱️  Duration: {trajectory[-1]['time']:.1f}s")
            
            # LOITER delays
            loiter_delays = drone_data.get('loiter_delays', [])
            if loiter_delays:
                total_loiter = sum(delay['duration'] for delay in loiter_delays)
                status_lines.append(f"   ⏸️  Wait Time: {total_loiter:.1f}s")
            
            # Current status
            if current_pos:
                phase_name = UILabels.PHASE_NAMES.get(current_pos.get('phase', FlightPhase.AUTO), "Executing")
                status_lines.append(f"   🎯 Phase: {phase_name}")
                status_lines.append(f"   📍 Position: ({current_pos['x']:.1f}, {current_pos['y']:.1f}, {current_pos['z']:.1f})")
            else:
                status_lines.append(f"   🎯 Status: {UILabels.STANDBY}")
            
            status_lines.append("")
        
        self.control_panel.update_status_text("\n".join(status_lines))
    
    def _update_warning_display(self, warnings: List[Dict]) -> None:
        """Update collision warning display"""
        if not self.control_panel:
            return
        
        if not warnings:
            self.control_panel.update_warning_text("✅ Flight safe, no collision risk", 'safe')
        else:
            warning_lines = [f"⚠️ Detected {len(warnings)} collision warnings!\n"]
            
            for i, warning in enumerate(warnings, 1):
                severity_text = "🚨 CRITICAL" if warning['severity'] == 'critical' else "⚠️ WARNING"
                warning_lines.append(f"{severity_text} {i}:")
                warning_lines.append(f"  🔄 {warning['drone1']} ↔ {warning['drone2']}")
                warning_lines.append(f"  📏 Distance: {warning['distance']:.2f}m")
                warning_lines.append(f"  🛡️ Safety: {self.safety_config.safety_distance:.1f}m")
                warning_lines.append(f"  ⏰ Time: {warning['time']:.1f}s\n")
            
            self.control_panel.update_warning_text("\n".join(warning_lines), 'danger')
    
    def _generate_modified_missions(self, loiter_commands: Dict[str, float]) -> None:
        """Generate modified mission files with LOITER commands"""
        for drone_id, loiter_time in loiter_commands.items():
            if drone_id in self.drones:
                waypoints = self.drones[drone_id]['waypoints']
                loiter_list = [{'time': loiter_time}] if loiter_time > 0 else None
                
                mission_lines = self.qgc_generator.generate_complete_mission(
                    drone_id, waypoints, loiter_list
                )
                
                self.modified_missions[drone_id] = mission_lines
                logger.info(f"Generated modified mission for {drone_id} with {loiter_time:.1f}s LOITER")
    
    def export_modified_missions(self) -> None:
        """Export modified mission files"""
        if not self.modified_missions:
            self.main_window.show_info(UILabels.EXPORT_INFO, "No modified mission files to export")
            return
        
        export_dir = filedialog.askdirectory(title="Select Export Directory")
        if not export_dir:
            return
        
        exported_files = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for drone_id, mission_lines in self.modified_missions.items():
            filename = f"{drone_id}_{SimulatorConfig.MISSION_FILE_PREFIX}_{timestamp}.waypoints"
            filepath = f"{export_dir}/{filename}"
            
            try:
                with open(filepath, 'w', encoding=SimulatorConfig.EXPORT_ENCODING) as f:
                    f.write('\n'.join(mission_lines))
                
                exported_files.append(filename)
                logger.info(f"Exported modified mission: {filepath}")
                
            except Exception as e:
                logger.error(f"Failed to export {drone_id} mission: {e}")
        
        if exported_files:
            self.main_window.show_info(
                UILabels.EXPORT_SUCCESS,
                f"Successfully exported {len(exported_files)} modified mission files to:\n{export_dir}"
            )
        else:
            self.main_window.show_error("Export Failed", "Failed to export any mission files")
    
    def export_collision_log(self) -> None:
        """Export collision log"""
        if not self.collision_logger:
            self.main_window.show_info(UILabels.EXPORT_INFO, "No collision events to export")
            return
        
        export_file = filedialog.asksaveasfilename(
            title="Save Collision Log",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if export_file:
            result = self.collision_logger.export_collision_log(export_file)
            if result:
                stats = self.collision_logger.get_collision_statistics()
                self.main_window.show_info(
                    UILabels.EXPORT_SUCCESS,
                    f"Collision log exported successfully to:\n{result}\n\n"
                    f"Total events: {stats['total_events']}\n"
                    f"Critical: {stats['critical_events']}\n"
                    f"Warnings: {stats['warning_events']}"
                )
            else:
                self.main_window.show_error("Export Failed", "Failed to export collision log")
    
    def analyze_collisions(self) -> None:
        """Analyze trajectory conflicts"""
        if not self.drones:
            self.main_window.show_info("Analysis", "No drone data available for analysis")
            return
        
        logger.info("🔍 Analyzing trajectory conflicts")
        
        conflicts = self.collision_system.analyze_trajectory_conflicts(self.drones)
        
        if conflicts:
            # Generate modified missions
            for conflict in conflicts:
                waiting_drone = conflict['waiting_drone']
                if waiting_drone not in self.modified_missions:
                    waypoints = self.drones[waiting_drone]['waypoints']
                    mission_lines = self.qgc_generator.generate_mission_with_conflicts(
                        waiting_drone, waypoints, [conflict]
                    )
                    self.modified_missions[waiting_drone] = mission_lines
            
            self.main_window.show_info(
                "Conflict Analysis",
                f"Found {len(conflicts)} trajectory conflicts\n"
                f"Generated {len(self.modified_missions)} modified missions\n"
                f"Use 'Export Modified Missions' to save files"
            )
        else:
            self.main_window.show_info("Conflict Analysis", "No trajectory conflicts detected")
    
    def clear_warnings(self) -> None:
        """Clear collision warnings"""
        self.collision_system.clear_warnings()
        self.collision_logger.clear_events()
        self._update_warning_display([])
        logger.info("🧹 Cleared collision warnings")
    
    # View control methods
    def set_top_view(self) -> None:
        if self.plot_manager:
            self.plot_manager.set_view_mode('top')
    
    def set_side_view(self) -> None:
        if self.plot_manager:
            self.plot_manager.set_view_mode('side')
    
    def set_3d_view(self) -> None:
        if self.plot_manager:
            self.plot_manager.set_view_mode('3d')
    
    # Control panel event handlers
    def on_time_change(self) -> None:
        """Handle time slider change"""
        if not self.is_playing:
            new_time = self.control_panel.get_variable_value('time_var')
            if new_time is not None:
                self.current_time = new_time
                self.control_panel.update_time_display(self.current_time, self.max_time)
                self._update_status_display()
                self._update_3d_plot()
    
    def on_speed_change(self) -> None:
        """Handle speed change"""
        new_speed = self.control_panel.get_variable_value('speed_var')
        if new_speed is not None:
            self.time_scale = new_speed
            logger.debug(f"Speed changed to {self.time_scale:.1f}x")
    
    def on_safety_change(self) -> None:
        """Handle safety distance change"""
        new_safety = self.control_panel.get_variable_value('safety_var')
        if new_safety is not None:
            self.safety_config.safety_distance = new_safety
            if not self.is_playing:
                self._update_3d_plot()
            logger.debug(f"Safety distance changed to {new_safety:.1f}m")
    
    def on_closing(self) -> None:
        """Handle application closing"""
        logger.info("🚪 Application closing")
        
        self.stop_simulation()
        
        # Export collision log if events exist
        if self.collision_logger and len(self.collision_logger) > 0:
            response = self.main_window.ask_yes_no(
                "Export Collision Log",
                f"Found {len(self.collision_logger)} collision events.\n"
                "Would you like to export the collision log before exiting?"
            )
            
            if response:
                try:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    log_file = f"collision_log_{timestamp}.json"
                    result = self.collision_logger.export_collision_log(log_file)
                    if result:
                        self.main_window.show_info("Export Success", f"Collision log saved to: {result}")
                except Exception as e:
                    logger.error(f"Failed to export collision log on exit: {e}")
        
        self._cleanup()
        self.main_window.destroy()
    
    def _cleanup(self) -> None:
        """Cleanup resources"""
        logger.info("🧹 Cleaning up resources")
        
        self._stop_animation()
        
        # Close matplotlib figures
        try:
            import matplotlib.pyplot as plt
            plt.close('all')
        except:
            pass
        
        logger.info("✅ Cleanup completed")


# Module test
if __name__ == "__main__":
    # Basic module test
    logging.basicConfig(level=logging.DEBUG)
    
    try:
        logger.info("🧪 Testing AdvancedDroneSimulator module")
        simulator = AdvancedDroneSimulator()
        logger.info("✅ Module test passed")
    except Exception as e:
        logger.error(f"❌ Module test failed: {e}")
        raise