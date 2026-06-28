import logging
from validator.schema import MissionPlan
from robot.base import BaseRobotController

logger = logging.getLogger(__name__)

class MissionExecutor:
    """
    Deterministic executor that translates a validated MissionPlan into 
    concrete commands for a RobotController.
    This layer contains no AI reasoning. The same JSON always produces the same behavior.
    """
    def __init__(self, robot: BaseRobotController, waypoints_config: dict):
        self.robot = robot
        self.waypoints = waypoints_config
        
    def execute(self, plan: MissionPlan) -> None:
        logger.info("=" * 50)
        logger.info(f"🚦 STARTING MISSION EXECUTION")
        logger.info(f"Mission Type: {plan.mission_type}")
        logger.info(f"Route: {plan.route}")
        logger.info(f"Loops: {plan.loops}")
        logger.info(f"Speed: {plan.speed} m/s")
        logger.info("=" * 50)
        
        # Resolve route to actual waypoint coordinates
        route_waypoints = self.waypoints.get("routes", {}).get(plan.route, [])
        if not route_waypoints:
            logger.error(f"Route '{plan.route}' has no waypoints defined!")
            return
            
        for loop_idx in range(1, plan.loops + 1):
            logger.info(f"🔄 Starting Loop {loop_idx}/{plan.loops}...")
            
            for wp in route_waypoints:
                name = wp.get("name", "unknown")
                x = wp.get("x", 0.0)
                y = wp.get("y", 0.0)
                theta = wp.get("theta", 0.0)
                
                # Deterministic command execution
                success = self.robot.navigate_to(name, x, y, theta, plan.speed)
                if not success:
                    logger.error(f"❌ Failed to navigate to {name}. Aborting mission.")
                    self.robot.stop()
                    return
                    
            logger.info(f"✅ Loop {loop_idx} completed.")
            
        if plan.return_home:
            logger.info("🏠 Returning home...")
            home_wp = self.waypoints.get("home", {"x": 0.0, "y": 0.0, "theta": 0.0})
            self.robot.navigate_to("home", home_wp["x"], home_wp["y"], home_wp["theta"], plan.speed)
            
        logger.info("=" * 50)
        logger.info(f"🏁 MISSION COMPLETE")
        logger.info("=" * 50)
