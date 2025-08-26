#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
3D Plot Manager Module
Advanced 3D visualization with Blender-style collision markers and mouse controls
"""

import tkinter as tk
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional, Callable
from config.settings import SimulatorConfig, AxisLabels, FlightPhase, TakeoffConfig

logger = logging.getLogger(__name__)

class Plot3DManager:
    """
    Advanced 3D plot manager with professional visualization
    Features mouse wheel zoom, view controls, and Blender-style collision markers
    """
    
    def __init__(self, parent: tk.Widget):
        self.parent = parent
        self.fig: Optional[plt.Figure] = None
        self.ax: Optional[plt.Axes] = None
        self.canvas: Optional[FigureCanvasTkAgg] = None
        self.toolbar: Optional[NavigationToolbar2Tk] = None
        
        # Plot data
        self.drone_data: Dict = {}
        self.collision_warnings: List[Dict] = []
        self.current_time: float = 0.0
        self.safety_distance: float = 5.0
        
        # Callbacks
        self.callbacks: Dict[str, Callable] = {}
        
        # View settings
        self.view_settings = {
            'elevation': 90,
            'azimuth': 0,
            'auto_fit': True,
            'margin': 50
        }
        
        logger.info("3D Plot Manager initialized")
    
    def register_callback(self, event_name: str, callback: Callable) -> None:
        """Register callback for plot events"""
        self.callbacks[event_name] = callback
        logger.debug(f"Registered plot callback: {event_name}")
    
    def setup_plot(self) -> tk.Frame:
        """
        Setup advanced 3D plot with professional styling
        
        Returns:
            Container frame for the plot
        """
        logger.info("Setting up 3D plot")
        
        # Use dark background style
        plt.style.use('dark_background')
        
        # Create high resolution figure
        self.fig = plt.figure(
            figsize=SimulatorConfig.FIGURE_SIZE,
            facecolor=SimulatorConfig.UI_COLORS['background'],
            dpi=SimulatorConfig.DPI
        )
        
        # Create 3D subplot
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        # Configure plot appearance
        self._setup_plot_style()
        
        # Create container frame
        plot_container = tk.Frame(self.parent, bg=SimulatorConfig.UI_COLORS['background'])
        plot_container.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas
        canvas_frame = tk.Frame(plot_container, bg=SimulatorConfig.UI_COLORS['background'])
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = FigureCanvasTkAgg(self.fig, canvas_frame)
        
        # Setup custom toolbar
        self._setup_custom_toolbar(canvas_frame)
        
        # Pack canvas
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Enable mouse interactions
        self._enable_mouse_controls()
        
        # Set initial view
        self.set_view_mode('top')
        
        logger.info("3D plot setup completed")
        return plot_container
    
    def _setup_plot_style(self) -> None:
        """Setup professional plot styling"""
        # Background and colors
        self.ax.set_facecolor(SimulatorConfig.UI_COLORS['background'])
        self.fig.patch.set_facecolor(SimulatorConfig.UI_COLORS['background'])
        
        # Grid
        self.ax.grid(True, alpha=0.3, color='#404040', linewidth=0.5)
        
        # Axis labels (English)
        self.ax.set_xlabel(AxisLabels.X_AXIS, fontsize=12, color=SimulatorConfig.UI_COLORS['accent'], labelpad=10)
        self.ax.set_ylabel(AxisLabels.Y_AXIS, fontsize=12, color=SimulatorConfig.UI_COLORS['accent'], labelpad=10)
        self.ax.set_zlabel(AxisLabels.Z_AXIS, fontsize=12, color=SimulatorConfig.UI_COLORS['accent'], labelpad=10)
        
        # Title
        self.ax.set_title(AxisLabels.TITLE, fontsize=14, color=SimulatorConfig.UI_COLORS['text'], pad=20)
        
        # Tick parameters
        self.ax.tick_params(colors='#888888', labelsize=10)
        
        # Axis panes (transparent)
        for pane in [self.ax.xaxis.pane, self.ax.yaxis.pane, self.ax.zaxis.pane]:
            pane.fill = False
            pane.set_edgecolor('#404040')
            pane.set_alpha(0.1)
        
        logger.debug("Plot style configured")
    
    def _setup_custom_toolbar(self, parent: tk.Widget) -> None:
        """Setup custom toolbar with view controls"""
        toolbar_frame = tk.Frame(parent, bg='#3a3a3a', height=40)
        toolbar_frame.pack(side=tk.TOP, fill=tk.X)
        toolbar_frame.pack_propagate(False)
        
        # Standard matplotlib toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.configure(bg='#3a3a3a')
        
        # Custom view controls
        custom_frame = tk.Frame(toolbar_frame, bg='#3a3a3a')
        custom_frame.pack(side=tk.RIGHT, padx=10)
        
        # View buttons
        view_buttons = [
            ("Top View", 'top'),
            ("Side View", 'side'),
            ("3D View", '3d'),
            ("Fit All", 'fit')
        ]
        
        for text, mode in view_buttons:
            btn = tk.Button(
                custom_frame,
                text=text,
                command=lambda m=mode: self.set_view_mode(m),
                bg='#007bff',
                fg='white',
                font=('Arial', 8),
                relief=tk.FLAT,
                borderwidth=1
            )
            btn.pack(side=tk.LEFT, padx=2)
        
        logger.debug("Custom toolbar created")
    
    def _enable_mouse_controls(self) -> None:
        """Enable mouse wheel zoom and other controls"""
        def on_scroll(event):
            if event.inaxes == self.ax:
                # Get current axis limits
                xlim = self.ax.get_xlim()
                ylim = self.ax.get_ylim()
                zlim = self.ax.get_zlim()
                
                # Zoom factor
                scale_factor = 1.1 if event.button == 'down' else 1/1.1
                
                # Calculate new limits around center
                x_center = (xlim[0] + xlim[1]) / 2
                y_center = (ylim[0] + ylim[1]) / 2
                z_center = (zlim[0] + zlim[1]) / 2
                
                x_range = (xlim[1] - xlim[0]) * scale_factor / 2
                y_range = (ylim[1] - ylim[0]) * scale_factor / 2
                z_range = (zlim[1] - zlim[0]) * scale_factor / 2
                
                # Set new limits
                self.ax.set_xlim(x_center - x_range, x_center + x_range)
                self.ax.set_ylim(y_center - y_range, y_center + y_range)
                self.ax.set_zlim(max(0, z_center - z_range), z_center + z_range)
                
                self.canvas.draw_idle()
        
        # Connect mouse events
        self.canvas.mpl_connect('scroll_event', on_scroll)
        
        # Double-click to reset view
        def on_double_click(event):
            if event.inaxes == self.ax and event.dblclick:
                self.fit_view()
        
        self.canvas.mpl_connect('button_press_event', on_double_click)
        
        logger.debug("Mouse controls enabled")
    
    def set_view_mode(self, mode: str) -> None:
        """
        Set predefined view mode
        
        Args:
            mode: View mode ('top', 'side', '3d', 'fit')
        """
        if mode == 'top':
            self.ax.view_init(elev=90, azim=0)
            self.view_settings.update({'elevation': 90, 'azimuth': 0})
        elif mode == 'side':
            self.ax.view_init(elev=0, azim=0)
            self.view_settings.update({'elevation': 0, 'azimuth': 0})
        elif mode == '3d':
            self.ax.view_init(elev=30, azim=45)
            self.view_settings.update({'elevation': 30, 'azimuth': 45})
        elif mode == 'fit':
            self.fit_view()
            return
        
        self.canvas.draw_idle()
        logger.debug(f"View mode set to: {mode}")
    
    def fit_view(self) -> None:
        """Fit view to show all data"""
        if not self.drone_data:
            return
        
        # Collect all coordinates
        all_x, all_y, all_z = [], [], []
        
        for drone_data in self.drone_data.values():
            trajectory = drone_data.get('trajectory', [])
            if trajectory:
                all_x.extend([p['x'] for p in trajectory])
                all_y.extend([p['y'] for p in trajectory])
                all_z.extend([p['z'] for p in trajectory])
        
        if all_x and all_y and all_z:
            margin = self.view_settings['margin']
            self.ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
            self.ax.set_ylim(min(all_y) - margin, max(all_y) + margin)
            self.ax.set_zlim(0, max(all_z) + margin)
            
            self.canvas.draw_idle()
            logger.debug("View fitted to data")
    
    def update_plot(self, drone_data: Dict, collision_warnings: List[Dict], 
                   current_time: float, safety_distance: float) -> None:
        """
        Update the 3D plot with current data
        
        Args:
            drone_data: Dictionary containing drone trajectory data
            collision_warnings: List of current collision warnings
            current_time: Current simulation time
            safety_distance: Current safety distance setting
        """
        # Store data
        self.drone_data = drone_data
        self.collision_warnings = collision_warnings
        self.current_time = current_time
        self.safety_distance = safety_distance
        
        # Clear and redraw
        self.ax.clear()
        self._setup_plot_style()
        
        if not drone_data:
            self._add_info_text()
            self.canvas.draw_idle()
            return
        
        # Draw trajectories and drones
        self._draw_trajectories()
        self._draw_current_positions()
        self._draw_collision_warnings()
        
        # Auto-fit view if enabled
        if self.view_settings['auto_fit']:
            self.fit_view()
        
        # Add information text
        self._add_info_text()
        
        self.canvas.draw_idle()
    
    def _draw_trajectories(self) -> None:
        """Draw drone trajectories"""
        for drone_id, data in self.drone_data.items():
            trajectory = data.get('trajectory', [])
            color = data.get('color', '#ffffff')
            
            if not trajectory:
                continue
            
            # Extract coordinates
            x_coords = [p['x'] for p in trajectory]
            y_coords = [p['y'] for p in trajectory]
            z_coords = [p['z'] for p in trajectory]
            
            # Draw complete trajectory (dashed line)
            self.ax.plot(x_coords, y_coords, z_coords,
                        color=color, linewidth=1.5, alpha=0.4, linestyle='--',
                        label=f'{drone_id} Planned')
            
            # Draw waypoints
            self.ax.scatter(x_coords, y_coords, z_coords,
                           color=color, s=25, alpha=0.6, marker='.')
            
            # Draw flown path (solid line)
            flown_path = self._get_flown_path(trajectory, self.current_time)
            if len(flown_path) > 1:
                flown_x = [p['x'] for p in flown_path]
                flown_y = [p['y'] for p in flown_path]
                flown_z = [p['z'] for p in flown_path]
                self.ax.plot(flown_x, flown_y, flown_z,
                            color=color, linewidth=4, alpha=0.9,
                            label=f'{drone_id} Flown')
    
    def _draw_current_positions(self) -> None:
        """Draw current drone positions with models"""
        for drone_id, data in self.drone_data.items():
            trajectory = data.get('trajectory', [])
            color = data.get('color', '#ffffff')
            
            if not trajectory:
                continue
            
            # Get current position
            current_pos = self._interpolate_position(trajectory, self.current_time)
            if current_pos:
                self._draw_drone_model(current_pos, color, drone_id)
    
    def _draw_drone_model(self, position: Dict, color: str, drone_id: str) -> None:
        """Draw detailed drone model"""
        x, y, z = position['x'], position['y'], position['z']
        size = 2.0
        
        # Get flight phase
        phase = position.get('phase', FlightPhase.AUTO)
        
        if phase == FlightPhase.TAXI:
            # Ground taxi: small square
            self.ax.scatter([x], [y], [z], s=100, c=[color], marker='s',
                           alpha=0.8, edgecolors='white', linewidth=1)
        elif phase == FlightPhase.TAKEOFF:
            # Taking off: triangle
            self.ax.scatter([x], [y], [z], s=150, c=[color], marker='^',
                           alpha=0.9, edgecolors='white', linewidth=2)
        else:
            # Normal flight: detailed quadcopter model
            # Main body
            self.ax.scatter([x], [y], [z], s=200, c=[color], marker='s',
                           alpha=0.9, edgecolors='white', linewidth=2)
            
            # Rotor arms and props
            arms = [
                (x + size, y, z + 0.2),
                (x - size, y, z + 0.2),
                (x, y + size, z + 0.2),
                (x, y - size, z + 0.2)
            ]
            
            # Draw rotors
            arm_x, arm_y, arm_z = zip(*arms)
            self.ax.scatter(arm_x, arm_y, arm_z, s=60, c=[color]*4,
                           marker='o', alpha=0.8, edgecolors='white', linewidth=1)
            
            # Draw arms
            for arm_x, arm_y, arm_z in arms:
                self.ax.plot([x, arm_x], [y, arm_y], [z, arm_z],
                            color=color, linewidth=2.5, alpha=0.8)
        
        # Drone label
        label = drone_id.split('_')[-1]
        self.ax.text(x, y, z + size + 2, label, fontsize=11, color='white',
                    weight='bold', ha='center', va='bottom')
        
        # Altitude indicator line
        if z > 0.1:
            self.ax.plot([x, x], [y, y], [0, z],
                        color=color, linewidth=1, alpha=0.3, linestyle=':')
    
    def _draw_collision_warnings(self) -> None:
        """Draw Blender-style collision warnings"""
        for warning in self.collision_warnings:
            drone1, drone2 = warning['drone1'], warning['drone2']
            
            # Get current positions
            pos1 = self._get_current_drone_position(drone1)
            pos2 = self._get_current_drone_position(drone2)
            
            if pos1 and pos2:
                # Red warning line (Blender-style)
                self.ax.plot([pos1['x'], pos2['x']],
                            [pos1['y'], pos2['y']],
                            [pos1['z'], pos2['z']],
                            color='red', linewidth=4, alpha=0.8)
                
                # Collision point marker
                mid_pos = warning['position']
                marker_size = 500 if warning['severity'] == 'critical' else 300
                
                self.ax.scatter([mid_pos[0]], [mid_pos[1]], [mid_pos[2]],
                               s=marker_size, c='red', marker='X',
                               alpha=0.9, edgecolors='white', linewidth=3)
                
                # Distance label
                distance_text = f"{warning['distance']:.1f}m"
                self.ax.text(mid_pos[0], mid_pos[1], mid_pos[2] + 2, distance_text,
                            fontsize=10, color='red', weight='bold',
                            ha='center', va='bottom')
    
    def _get_current_drone_position(self, drone_id: str) -> Optional[Dict]:
        """Get current position of a specific drone"""
        if drone_id not in self.drone_data:
            return None
        
        trajectory = self.drone_data[drone_id].get('trajectory', [])
        return self._interpolate_position(trajectory, self.current_time)
    
    def _interpolate_position(self, trajectory: List[Dict], time: float) -> Optional[Dict]:
        """Interpolate position at given time"""
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
                    'time': time,
                    'phase': trajectory[i].get('phase', FlightPhase.AUTO)
                }
        
        return None
    
    def _get_flown_path(self, trajectory: List[Dict], current_time: float) -> List[Dict]:
        """Get the portion of trajectory already flown"""
        flown_path = []
        
        for point in trajectory:
            if point['time'] <= current_time:
                flown_path.append(point)
            else:
                # Add current interpolated position
                current_pos = self._interpolate_position(trajectory, current_time)
                if current_pos:
                    flown_path.append(current_pos)
                break
        
        return flown_path
    
    def _add_info_text(self) -> None:
        """Add information text overlay"""
        info_lines = [
            f"Time: {self.current_time:.1f}s",
            f"Drones: {len(self.drone_data)}/{SimulatorConfig.MAX_DRONES}",
            f"Safety Distance: {self.safety_distance:.1f}m"
        ]
        
        # Add formation spacing info if available
        formation_spacing = getattr(TakeoffConfig(), 'formation_spacing', 6.0)
        info_lines.append(f"Formation Spacing: {formation_spacing:.1f}m")
        
        # Add collision count
        if self.collision_warnings:
            info_lines.append(f"⚠️ Collisions: {len(self.collision_warnings)}")
        
        # Display info
        for i, line in enumerate(info_lines):
            color = '#ff5722' if '⚠️' in line else SimulatorConfig.UI_COLORS['accent']
            self.ax.text2D(0.02, 0.98 - i*0.04, line,
                          transform=self.ax.transAxes, fontsize=10,
                          color=color, weight='bold')
    
    def add_custom_marker(self, position: Tuple[float, float, float],
                         text: str, color: str = 'yellow', size: int = 100) -> None:
        """Add custom marker to the plot"""
        x, y, z = position
        self.ax.scatter([x], [y], [z], s=size, c=color, marker='*',
                       alpha=0.9, edgecolors='white', linewidth=2)
        
        if text:
            self.ax.text(x, y, z + 3, text, fontsize=9, color=color,
                        weight='bold', ha='center', va='bottom')
    
    def clear_plot(self) -> None:
        """Clear the plot"""
        self.ax.clear()
        self._setup_plot_style()
        self.canvas.draw_idle()
        logger.debug("Plot cleared")
    
    def save_plot(self, filename: str, dpi: int = 300) -> bool:
        """
        Save current plot to file
        
        Args:
            filename: Output filename
            dpi: Resolution for saved image
            
        Returns:
            True if successful
        """
        try:
            self.fig.savefig(filename, dpi=dpi, bbox_inches='tight',
                            facecolor=SimulatorConfig.UI_COLORS['background'])
            logger.info(f"Plot saved to: {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to save plot: {e}")
            return False
    
    def get_view_settings(self) -> Dict:
        """Get current view settings"""
        return self.view_settings.copy()
    
    def set_view_settings(self, settings: Dict) -> None:
        """Set view settings"""
        self.view_settings.update(settings)
        self.ax.view_init(elev=settings.get('elevation', 30),
                         azim=settings.get('azimuth', 45))
        self.canvas.draw_idle()


# Example usage and testing
if __name__ == "__main__":
    # Test 3D plot manager
    logging.basicConfig(level=logging.DEBUG)
    
    # Create test window
    root = tk.Tk()
    root.title("3D Plot Manager Test")
    root.geometry("1200x800")
    root.configure(bg=SimulatorConfig.UI_COLORS['background'])
    
    # Create plot manager
    plot_manager = Plot3DManager(root)
    
    # Setup plot
    plot_frame = plot_manager.setup_plot()
    
    # Create test data
    test_data = {
        'Drone_1': {
            'trajectory': [
                {'x': 0, 'y': 0, 'z': 0, 'time': 0, 'phase': FlightPhase.TAXI},
                {'x': 10, 'y': 10, 'z': 10, 'time': 5, 'phase': FlightPhase.AUTO},
                {'x': 20, 'y': 0, 'z': 15, 'time': 10, 'phase': FlightPhase.AUTO}
            ],
            'color': '#FF4444'
        },
        'Drone_2': {
            'trajectory': [
                {'x': 5, 'y': 0, 'z': 0, 'time': 0, 'phase': FlightPhase.TAXI},
                {'x': 15, 'y': 15, 'z': 10, 'time': 5, 'phase': FlightPhase.AUTO},
                {'x': 25, 'y': 5, 'z': 15, 'time': 10, 'phase': FlightPhase.AUTO}
            ],
            'color': '#44FF44'
        }
    }
    
    # Update plot with test data
    plot_manager.update_plot(test_data, [], 2.5, 5.0)
    
    print("3D Plot Manager test - Close window to exit")
    
    # Run test
    root.mainloop()