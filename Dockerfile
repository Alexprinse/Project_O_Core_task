FROM osrf/ros:humble-desktop

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV TURTLEBOT3_MODEL=waffle_pi
ENV LIBGL_ALWAYS_SOFTWARE=1
ENV GAZEBO_MODEL_PATH=/opt/ros/humble/share/:/root/.gazebo/models

WORKDIR /app

# 1. Install system tools, Gazebo, Nav2, and SLAM packages
# Note: package is 'gazebo' on Ubuntu 22.04 Jammy (not 'gazebo11')
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-pip \
    git \
    curl \
    ca-certificates \
    gazebo \
    ros-humble-gazebo-ros-pkgs \
    ros-humble-turtlebot3 \
    ros-humble-turtlebot3-description \
    ros-humble-turtlebot3-simulations \
    ros-humble-navigation2 \
    ros-humble-nav2-bringup \
    ros-humble-slam-toolbox \
    ros-humble-nav2-simple-commander \
    && rm -rf /var/lib/apt/lists/*

# 2. Setup Gazebo model cache directory inside Docker
RUN mkdir -p /root/.gazebo/models && \
    echo '<?xml version="1.0"?><gazebo><model_database>http://localhost:8080</model_database></gazebo>' > /root/.gazebo/config

# 3. Clone and cache the AWS warehouse models inside the image (runs 100% offline)
RUN git clone https://github.com/aws-robotics/aws-robomaker-small-warehouse-world.git /tmp/aws_warehouse && \
    cp -r /tmp/aws_warehouse/models/* /root/.gazebo/models/ && \
    rm -rf /tmp/aws_warehouse

# 4. Cache TurtleBot3 models into /root/.gazebo/models/ so Gazebo finds them offline.
# We use find to locate the actual model dirs regardless of exact install path.
RUN find /opt/ros/humble/share/turtlebot3_gazebo/models/ -mindepth 1 -maxdepth 1 -type d \
      -exec cp -r {} /root/.gazebo/models/ \; 2>/dev/null || true && \
    find /opt/ros/humble/share/turtlebot3_description/ -mindepth 0 -maxdepth 0 -type d \
      -exec cp -r {} /root/.gazebo/models/turtlebot3_description \; 2>/dev/null || true

# 4.5. Cache standard target models locally for offline Vision AI tasks (Challenge 3)
RUN for model in person_standing beer suv bus car_wheel mailbox stop_light; do \
      mkdir -p /root/.gazebo/models/$model && \
      curl -sSL http://models.gazebosim.org/$model/model.tar.gz | tar -xz -C /root/.gazebo/models/; \
    done

# 5. Copy python requirements and install them
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt


# 6. Copy the project code (yolov8n.pt is included here)
COPY . .

# 6.5. Pre-download YOLOv8 nano weights into the image for offline use (Challenge 3)
# ultralytics downloads yolov8n.pt automatically by name - no local file needed.
# The weights are cached to /root/.ultralytics/ inside the image.
ENV YOLO_CONFIG_DIR=/root/.config/Ultralytics
RUN mkdir -p /root/.config/Ultralytics && \
    python3 -c "from ultralytics import YOLO; YOLO('yolov8n.pt')" && \
    echo 'YOLOv8 preload OK'

# 7. Set up persistent environment sourcing
RUN echo "source /opt/ros/humble/setup.bash" >> /root/.bashrc && \
    echo "source /usr/share/gazebo/setup.sh" >> /root/.bashrc && \
    echo "export GAZEBO_MODEL_PATH=\$GAZEBO_MODEL_PATH:/opt/ros/humble/share/:/root/.gazebo/models" >> /root/.bashrc && \
    echo "export TURTLEBOT3_MODEL=waffle_pi" >> /root/.bashrc && \
    echo "export LIBGL_ALWAYS_SOFTWARE=1" >> /root/.bashrc

# Default entrypoint starts bash so you can run commands interactively
CMD ["bash"]
