#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Advanced Drone Swarm Simulator v5.1 - Main Entry Point
Professional Edition with Collision Logging and Enhanced Features
"""

import sys
import os

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def main():
    """Main function with enhanced error handling"""
    try:
        # Setup logging first
        from utils.logging_config import setup_logging
        logger = setup_logging()
        logger.info("🚁 Advanced Drone Swarm Simulator v5.1 Starting")
        logger.info("🆕 New Features: Collision Logging, 6m Spacing, English UI, Mouse Zoom")
        
        # Setup matplotlib and Chinese font support
        import matplotlib
        matplotlib.use('TkAgg')
        
        import matplotlib.pyplot as plt
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        
        # High performance settings
        plt.rcParams['path.simplify'] = True
        plt.rcParams['path.simplify_threshold'] = 0.1
        plt.rcParams['agg.path.chunksize'] = 10000
        plt.rcParams['animation.html'] = 'jshtml'
        
        logger.info("✅ Environment setup complete")
        logger.info("🎯 Version Features: Collision Detection, Mouse Zoom, 2x2 6m Takeoff, LOITER Avoidance, Collision Logging")
        
        # Import and create simulator
        from simulator.drone_simulator import AdvancedDroneSimulator
        simulator = AdvancedDroneSimulator()
        simulator.run()
        
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("📦 Install dependencies: pip install -r requirements.txt")
        print("🖥️  GUI dependencies: Ensure tkinter is installed (usually comes with Python)")
        sys.exit(1)
    except Exception as e:
        print(f"💥 Program runtime error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()