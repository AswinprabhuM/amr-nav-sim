# Setup

Tested on Ubuntu 24.04 with ROS 2 Jazzy and Gazebo Harmonic (gz sim 8.11.0).

## Prerequisites

- ROS 2 Jazzy (`/opt/ros/jazzy`)
- Gazebo Harmonic
- ROS packages: `ros_gz_sim`, `ros_gz_bridge`, `robot_state_publisher`, `xacro`,
  `launch_ros` (the `exec_depend`s in `package.xml`)
- `colcon`

TODO: exact apt package names used to install these.

## Build

```bash
source /opt/ros/jazzy/setup.bash
cd <repo-root>
colcon build
source install/setup.bash
```

## Run

```bash
ros2 launch amr_sim sim.launch.py
# headless (no GUI):
ros2 launch amr_sim sim.launch.py gz_flags:="-s"
```

Drive the robot (TODO: not yet verified):

```bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.2}}"
```

## Verify

See [verification.md](verification.md).
