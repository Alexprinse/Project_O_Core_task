from pydantic import BaseModel, Field
from typing import Optional

class MissionPlan(BaseModel):
    """
    Pydantic schema defining the structured JSON expected from the LLM.
    This guarantees type safety and correct data extraction.
    """
    mission_type: str = Field(
        description="The type of mission, e.g., 'patrol', 'inspect', 'deliver'"
    )
    route: str = Field(
        description="The name of the route to follow"
    )
    loops: int = Field(
        default=1, 
        description="Number of times to execute the route"
    )
    speed: Optional[float] = Field(
        default=None, 
        description="The speed of the robot in meters per second"
    )
    return_home: bool = Field(
        default=True, 
        description="Whether the robot should return home after the mission"
    )
