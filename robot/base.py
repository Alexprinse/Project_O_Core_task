from abc import ABC, abstractmethod

class BaseRobotController(ABC):
    """
    Abstract interface for all robot controllers.
    Ensures that the LLM/Executor layer remains completely decoupled 
    from the actual robot hardware or simulator (ROS/Nav2).
    """
    
    @abstractmethod
    def navigate_to(self, target_name: str, x: float, y: float, theta: float, speed: float) -> bool:
        """
        Commands the robot to navigate to the specified coordinates.
        Returns True if successful, False otherwise.
        """
        pass
        
    @abstractmethod
    def stop(self) -> None:
        """
        Commands the robot to stop immediately.
        """
        pass
