# e-Yantra Krishi Cobot (ebot) Pipeline

The Omokai Robotics pipeline was originally developed and tested against the **e-Yantra Krishi Cobot** in addition to the TurtleBot3. The ebot relies on direct odometry and LiDAR-based proportional velocity control rather than the Nav2 stack.

This document covers how to run the pipeline natively with the e-Yantra robot.

---

## 1. Install Dependencies & Build Workspace

Before running the simulation, you must install the Ignition Gazebo dependencies and build the e-Yantra workspace.

```bash
# Install ebot dependencies
chmod +x ./eyrc_ws/requirements.sh
./eyrc_ws/requirements.sh

# Build the workspace
source /opt/ros/humble/setup.bash
cd eyrc_ws
colcon build
cd ..
```

---

## 2. Start the Simulation (Terminal 1 & 2)

**Terminal 1 (Launch World):**
```bash
source eyrc_ws/install/setup.bash
ros2 launch eyantra_warehouse task2.launch.py
```

**Terminal 2 (Spawn Robot):**
```bash
source eyrc_ws/install/setup.bash
ros2 launch ebot_description spawn_ebot.launch.py
```

---

## 3. Run the Pipeline Controller (Terminal 3)

Activate your Python virtual environment and run the pipeline specifically targeting the ebot:

```bash
source .venv/bin/activate
export GEMINI_API_KEY="your_gemini_api_key_here"

python3 main.py --prompt "Navigate the serpentine path" --ros --robot ebot
```

---

## 4. Configuration

The ebot uses its own dedicated waypoint and configuration file:
* **config/waypoints_ebot.yaml**: Contains the specific serpentine and corridor coordinates required for the ebot warehouse tasks.

---

## 5. Architecture Notes

The proportional control and LiDAR obstacle avoidance algorithms implemented in `robot/ebot_controller.py` are adapted from past work in the e-Yantra Robotics Competition 2025-26. Unlike Nav2, this uses a pure pursuit algorithm reacting dynamically to `/scan` (LiDAR) messages to navigate waypoints while dodging obstacles.
