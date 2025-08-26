# Advanced Drone Swarm Simulator v5.1 - Professional Edition

🚁 **Professional-grade drone swarm simulation system with advanced collision detection and 3D visualization**

![Version](https://img.shields.io/badge/version-5.1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)
![Status](https://img.shields.io/badge/status-stable-brightgreen.svg)

## 🆕 What's New in v5.1

- **🔍 Collision Event Logging**: Complete JSON-based collision documentation
- **📏 6-Meter Formation Spacing**: Enhanced safety with configurable 2x2 takeoff formation
- **🌍 English Professional Interface**: International-ready professional UI
- **🖱️ Mouse Wheel Zoom**: Interactive 3D navigation with zoom controls
- **🎨 Blender-Style Collision Markers**: Professional visual collision warnings
- **📦 Modular Architecture**: Clean, maintainable code structure

## 🚀 Key Features

### 🛡️ Advanced Safety Systems
- **Real-time Collision Detection**: Monitor drone separation every 0.1 seconds
- **Priority-based Conflict Resolution**: Lower-numbered drones have takeoff priority
- **Automatic LOITER Insertion**: Smart conflict avoidance with precise timing
- **Comprehensive Collision Logging**: JSON export with detailed event data

### 🎯 Professional Formation Flight
- **2x2 Takeoff Formation**: Configurable spacing (default: 6 meters)
- **Unified East Takeoff Area**: 50-meter offset from base coordinates
- **Realistic Flight Sequence**: Ground taxi → Takeoff → Hover → Mission → RTL
- **Earth Coordinate System**: Accurate lat/lon to meter conversion with curvature correction

### 📊 Advanced 3D Visualization
- **Professional 3D Rendering**: High-performance matplotlib-based visualization
- **Interactive Controls**: Mouse wheel zoom, view rotation, preset viewpoints
- **Real-time Trajectory Display**: Live drone positions with flight path history
- **Collision Warning System**: Red collision lines and distance markers

### 📁 File Format Support
- **QGC Waypoint Files**: Full QGroundControl .waypoints format support
- **CSV Import**: Flexible CSV parsing with automatic column detection
- **Mission Export**: Modified .waypoints files with LOITER commands
- **Collision Logs**: JSON format for analysis and reporting

## 📋 System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **RAM**: 4GB (recommended for 4-drone simulations)
- **Display**: 1920x1080 resolution (supports smaller screens)
- **OS**: Windows 10, macOS 10.14, or Ubuntu 18.04+

### Python Dependencies
```bash
numpy>=1.21.0       # Numerical computations
pandas>=1.3.0       # Data manipulation and CSV parsing
matplotlib>=3.5.0   # 3D plotting and visualization
psutil>=5.8.0       # System information (optional)
tkinter             # GUI framework (usually included with Python)
```

## 🛠️ Installation

### Quick Start
```bash
# Clone the repository
git clone https://github.com/drone-lab/advanced-drone-simulator.git
cd drone_simulator_v5.1

# Install dependencies
pip install -r requirements.txt

# Run the simulator
python main.py
```

### Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv drone_simulator_env

# Activate environment
# Windows:
drone_simulator_env\Scripts\activate
# Linux/macOS:
source drone_simulator_env/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run simulator
python main.py
```

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8 mypy

# Run tests
pytest tests/

# Format code
black .

# Type checking
mypy .
```

## 📂 Project Structure

```
drone_simulator_v5.1/
│
├── main.py                    # 🚀 Main entry point
├── requirements.txt           # 📦 Dependencies
├── README.md                 # 📚 This file
│
├── config/                   # ⚙️ Configuration
│   ├── __init__.py
│   └── settings.py           # Settings and constants
│
├── core/                     # 🧠 Core simulation logic
│   ├── __init__.py
│   ├── coordinate_system.py  # Earth coordinate conversions
│   ├── collision_logger.py   # Collision event logging (NEW)
│   ├── collision_avoidance.py # Collision detection & avoidance
│   └── flight_manager.py     # Takeoff management & waypoint generation
│
├── gui/                      # 🖥️ User interface
│   ├── __init__.py
│   ├── main_window.py        # Main window and menus
│   ├── control_panel.py      # Control panel UI
│   └── plot_manager.py       # 3D visualization
│
├── simulator/                # 🎮 Simulation engine
│   ├── __init__.py
│   ├── drone_simulator.py    # Main simulator class
│   └── file_parser.py        # QGC and CSV parsers
│
├── utils/                    # 🔧 Utilities
│   ├── __init__.py
│   └── logging_config.py     # Professional logging setup
│
└── tests/                    # 🧪 Test suite
    ├── __init__.py
    ├── test_coordinate.py
    ├── test_collision.py
    └── test_collision_logger.py
```

## 🎮 Usage Guide

### 1. Quick Start with Test Mission
1. **Launch**: Run `python main.py`
2. **Create Test Mission**: Click "Test" button or Ctrl+T
3. **Start Simulation**: Click Play ▶️ or press Space
4. **Monitor**: Watch 3D visualization and collision warnings

### 2. Loading Mission Files

#### QGC Waypoint Files
```python
# Load standard QGroundControl waypoint files
File → Load QGC Files
# Or press Ctrl+O
```

#### CSV Files
```python
# Supported CSV column names:
latitude, longitude, altitude
lat, lon, alt
x, y, z  # (where x=lon, y=lat, z=alt)
Latitude, Longitude, Altitude
```

### 3. Collision Analysis
- **Real-time Monitoring**: Red lines show collision risks
- **Export Collision Log**: Click 📊 button or Ctrl+L
- **View Statistics**: Check status panel for collision summary

### 4. View Controls
| Control | Action |
|---------|--------|
| **Mouse Wheel** | Zoom in/out |
| **Mouse Drag** | Rotate 3D view |
| **1** | Top view |
| **2** | Side view |
| **3** | 3D perspective |
| **F** | Fit all in view |
| **Double Click** | Reset view |

### 5. Keyboard Shortcuts
| Shortcut | Function |
|----------|----------|
| **Space** | Play/Pause simulation |
| **S** | Stop simulation |
| **Ctrl+R** | Reset simulation |
| **Ctrl+T** | Create test mission |
| **Ctrl+S** | Export modified missions |
| **Ctrl+L** | Export collision log |
| **F1** | Show help |
| **ESC** | Exit |

## 🔧 Configuration

### Formation Settings
```python
# config/settings.py
@dataclass
class TakeoffConfig:
    formation_spacing: float = 6.0    # Meters between drones
    takeoff_altitude: float = 10.0    # Initial climb altitude
    hover_time: float = 2.0           # Hover duration after takeoff
    east_offset: float = 50.0         # Takeoff area offset
```

### Safety Parameters
```python
@dataclass
class SafetyConfig:
    safety_distance: float = 5.0          # Minimum safe distance
    warning_distance: float = 8.0         # Warning threshold
    critical_distance: float = 3.0        # Critical collision threshold
    collision_check_interval: float = 0.1 # Check frequency (seconds)
```

## 📊 Output Files

### Modified Mission Files
- **Format**: QGroundControl .waypoints
- **Location**: User-selected directory
- **Naming**: `{DroneID}_modified_{timestamp}.waypoints`
- **Content**: Original mission + LOITER commands for collision avoidance

### Collision Logs
- **Format**: JSON
- **Location**: User-selected file
- **Content**: 
  ```json
  {
    "metadata": {
      "total_events": 5,
      "export_time": "2024-01-15T10:30:00",
      "simulation_version": "5.1.0",
      "statistics": { ... }
    },
    "collision_events": [
      {
        "timestamp": "2024-01-15T10:25:30",
        "simulation_time": 12.5,
        "drone1": "Drone_1",
        "drone2": "Drone_2", 
        "distance": 3.2,
        "severity": "warning",
        "position1": {"x": 10.5, "y": 20.3, "z": 15.0},
        "position2": {"x": 12.1, "y": 18.7, "z": 14.8}
      }
    ]
  }
  ```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test categories
pytest tests/test_collision.py
pytest tests/test_coordinate.py
```

### Test Categories
- **Unit Tests**: Individual module functionality
- **Integration Tests**: Cross-module interactions
- **GUI Tests**: User interface components
- **File I/O Tests**: File parsing and export

## 🐛 Troubleshooting

### Common Issues

#### 1. tkinter Not Found
```bash
# Linux/Ubuntu
sudo apt-get install python3-tk

# macOS (with Homebrew)
brew install python-tk

# Windows
# Reinstall Python with tkinter option checked
```

#### 2. Matplotlib Display Issues
```bash
# Try different backend
import matplotlib
matplotlib.use('TkAgg')
```

#### 3. Memory Issues with Large Simulations
- Reduce simulation time scale
- Use fewer trajectory points
- Close other applications
- Ensure 8GB+ RAM for complex missions

#### 4. File Import Errors
- Check CSV column names (see supported formats)
- Verify QGC file format (QGC WPL 110)
- Ensure proper encoding (UTF-8)

### Debug Mode
```bash
# Run with debug logging
python main.py --log-level DEBUG

# Check log files
tail -f logs/drone_simulator_*.log
```

## 🤝 Contributing

### Development Workflow
1. **Fork** the repository
2. **Create** feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** changes (`git commit -m 'Add amazing feature'`)
4. **Push** to branch (`git push origin feature/amazing-feature`)
5. **Open** Pull Request

### Code Style
- **Python**: Follow PEP 8
- **Formatting**: Use `black` formatter
- **Type Hints**: Use type annotations
- **Documentation**: Add docstrings for all functions

### Testing Requirements
- Unit tests for new features
- Integration tests for major changes
- Code coverage >80%
- All tests must pass

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Authors

- **Drone Path Planning Laboratory** - *Initial work and development*
- **Contributors** - See [CONTRIBUTORS.md](CONTRIBUTORS.md) for list of contributors

## 🙏 Acknowledgments

- **QGroundControl** - For waypoint file format specifications
- **matplotlib** - For excellent 3D plotting capabilities  
- **Python Community** - For amazing scientific computing ecosystem
- **Research Community** - For drone swarm algorithms and safety protocols

## 📞 Support

### Documentation
- **User Manual**: Press F1 in application or see [Wiki](wiki)
- **API Documentation**: Generated with Sphinx
- **Video Tutorials**: Available on [YouTube Channel](youtube)

### Community
- **Issues**: [GitHub Issues](issues)
- **Discussions**: [GitHub Discussions](discussions)
- **Discord**: [Join our server](discord)
- **Email**: contact@dronelab.example.com

### Professional Support
For commercial use, custom features, or professional support:
- **Enterprise Support**: enterprise@dronelab.example.com
- **Training Services**: Available for teams and organizations
- **Custom Development**: Tailored solutions for specific requirements

---

<div align="center">

**🚁 Advanced Drone Swarm Simulator v5.1 - Professional Edition**

*Empowering safer drone operations through advanced simulation*

[![Star](https://img.shields.io/github/stars/drone-lab/advanced-drone-simulator?style=social)](github)
[![Fork](https://img.shields.io/github/forks/drone-lab/advanced-drone-simulator?style=social)](github)
[![Watch](https://img.shields.io/github/watchers/drone-lab/advanced-drone-simulator?style=social)](github)

</div>