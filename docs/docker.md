# Docker Setup Guide — Omokai Robotics Mission Pipeline

This guide covers running the **entire simulation, ROS 2 Navigation stack, and Python LLM pipeline** inside Docker, with the Gazebo/RViz 3D windows forwarded to your host display via X11.

No local ROS 2, Gazebo, or Python environment installation is required — only Docker and an X server (already present on any Linux desktop).

---

## 1. Prerequisites

- Linux host (tested on Ubuntu 22.04 LTS)
- Docker Engine + Docker Compose plugin installed:
  ```bash
  docker --version
  docker compose version
  ```
  If missing, install via [Docker's official guide](https://docs.docker.com/engine/install/ubuntu/).
- A Gemini API key ([ai.google.dev](https://ai.google.dev)) — required for LLM-based prompt parsing (not needed for `--mock-llm` mode).

---

## 2. Clone the Repository

```bash
git clone https://github.com/Alexprinse/Project_O.git
cd Project_O
```

---

## 3. Build the Image (once)

```bash
docker compose build
```

This builds a single image containing ROS 2 Humble, Gazebo, Nav2, SLAM Toolbox, YOLOv8/Ultralytics, and all Python dependencies for the mission pipeline.

---

## 4. Grant Docker Access to Your Display (X11 Forwarding)

Run this once per host session, before starting any simulation container:

```bash
xhost +local:docker
```

This allows containers to render Gazebo/RViz windows on your host screen. It does not persist across reboots — re-run it if your display access breaks after a restart.

---

## 5. Export Your Gemini API Key

```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
```

Skip this step if you're only testing with `--mock-llm`.

---

## 6. Choose and Launch a Simulation Scenario

Each scenario maps to a specific `docker-compose` service. Run **one simulation service** per terminal session, matching the challenge you want to test:

| Scenario | Command |
|---|---|
| Core task / Challenge 1 & 3 — single robot, static map | `docker compose up simulation` |
| Challenge 2 & 3 — single robot, live SLAM mode | `docker compose up simulation-slam` |
| Challenge 1 —> 2-robot squad, static map | `docker compose up simulation-multi-2` |
| Challenge 1 —> 3-robot squad, static map | `docker compose up simulation-multi-3` |
| Challenge 1+2 —> 2-robot SLAM | `docker compose up simulation-multi-slam-2 multi-slam` |
| Challenge 1+2 —> 3-robot SLAM | `docker compose up simulation-multi-slam-3 multi-slam` |

> **Multi-robot SLAM note:** always run the `multi-slam` service alongside any `simulation-multi-slam-*` service — it starts a namespaced `slam_toolbox` instance per robot with correct TF remapping. Running SLAM services without it will cause map/frame contamination across robots.

Leave this terminal running — Gazebo and Nav2 will stay up in the foreground.

---

## 7. Run the Controller (separate terminal)

With a simulation service running, open a **second terminal** and start the controller container:

```bash
docker compose run controller
```

This drops you into a shell inside the container with ROS 2 and the Python environment already sourced.

### Run a mission prompt:

```bash
python3 main.py --prompt "split the route of warehouse_patrol between robot 1 and robot 2" --ros --robot turtlebot3
```

---

## 8. Example Prompts by Challenge

**Challenge 1 — Multi-Robot Squad Coordination**
```bash
python3 main.py --prompt "robot 1 and robot 2 patrol warehouse_patrol in column formation" --ros --robot turtlebot3
python3 main.py --prompt "robot 1 patrol top_side, robot 2 patrol bottom_side, and robot 3 do delivery" --ros --robot turtlebot3
```

**Challenge 2 — SLAM & Autonomous Navigation**
```bash
python3 main.py --prompt "go to right_end" --ros --robot turtlebot3
python3 main.py --prompt "go to x=1.92, y=2.20 and then go to x=1.76, y=-9.43" --ros --robot turtlebot3
```

**Challenge 3 — Vision AI Target Detection & Follow**
```bash
# In the controller container, spawn a target first:
python3 scripts/swap_object.py --object person --x 1.8 --y 7.0

# Then issue a follow prompt:
python3 main.py --prompt "go to right_end, then search and follow the bottle" --ros --robot turtlebot3
```

Open RViz → **Add → Image** → subscribe to `/camera/image_annotated` to view the live annotated camera feed with detection bounding boxes.

---

## 9. Offline / Mock Mode (No Simulator Required)

To test the LLM → JSON → validation pipeline without Gazebo, ROS 2, or a GPU:

```bash
docker build -t omokai-mission-pipeline .
docker run -it --rm omokai-mission-pipeline --prompt "Patrol the warehouse loop twice" --robot turtlebot3 --mock-llm
```

---

## 10. Shutting Down

Stop the controller shell with `exit`, then stop the simulation service in its terminal with `Ctrl+C`, followed by:

```bash
docker compose down
```

---

## 11. Troubleshooting

| Symptom | Fix |
|---|---|
| Gazebo/RViz window doesn't appear | Re-run `xhost +local:docker`; confirm `$DISPLAY` is set on host |
| `GEMINI_API_KEY` errors | Re-export the key in the terminal running `docker compose up`/`run`, or add it to a `.env` file read by Compose |
| Multi-robot maps overlapping/contaminated | Confirm the `multi-slam` service is running alongside any `simulation-multi-slam-*` service |
| Slow rendering / software fallback | Confirm host GPU drivers are installed; Gazebo will fall back to `llvmpipe` software rendering without them, which is expected on GPU-less machines but will be visibly slower |