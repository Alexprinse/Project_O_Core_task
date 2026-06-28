import time
import math
import logging
from .base import BaseRobotController

logger = logging.getLogger(__name__)

class MockRobotController(BaseRobotController):
    """
    A mock simulator for testing the mission pipeline natively on macOS 
    without needing ROS 2 or Gazebo installed.
    It simulates travel time based on distance and speed, and prints telemetry.
    """
    def __init__(self):
        # Assume robot starts at origin
        self.current_x = 0.0
        self.current_y = 0.0
        self.current_theta = 0.0
        
    def navigate_to(self, target_name: str, x: float, y: float, theta: float, speed: float) -> bool:
        logger.info(f"🚀 [MockRobot] Navigating to '{target_name}' ({x}, {y}) at {speed} m/s...")
        
        distance = math.sqrt((x - self.current_x)**2 + (y - self.current_y)**2)
        if distance > 0 and speed > 0:
            travel_time = distance / speed
            logger.info(f"   [MockRobot] Distance: {distance:.2f}m. Estimated travel time: {travel_time:.2f}s")
            
            # Simulate travel with small sleeps to show progress
            steps = 5
            sleep_per_step = travel_time / steps
            
            # Cap the sleep per step in mock mode to keep tests snappy
            if sleep_per_step > 0.5:
                sleep_per_step = 0.5 
                
            for i in range(1, steps + 1):
                time.sleep(sleep_per_step)
                logger.info(f"   [MockRobot] Progress: {int((i/steps)*100)}%...")
                
        self.current_x = x
        self.current_y = y
        self.current_theta = theta
        
        logger.info(f"✅ [MockRobot] Arrived at '{target_name}'.")
        return True
        
    def stop(self) -> None:
        logger.warning("🛑 [MockRobot] Emergency Stop triggered!")
