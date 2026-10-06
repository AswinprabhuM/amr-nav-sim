# Architecture

Everything below is taken from `src/amr_sim/urdf/amr.urdf.xacro`,
`src/amr_sim/launch/sim.launch.py` and `src/amr_sim/worlds/warehouse.sdf`.

## Nodes started by `sim.launch.py`

| Process | Package / executable | Role |
|---|---|---|
| Gazebo | `ros_gz_sim` / `gz_sim.launch.py` | Runs `warehouse.sdf` (`-r`, plus `gz_flags`) |
| `robot_state_publisher` | `robot_state_publisher` | Publishes `/robot_description` and the fixed-joint TFs (`use_sim_time: true`) |
| `create` | `ros_gz_sim` | Spawns model `amr` from `/robot_description` at x=0, y=0, z=0.15 |
| `parameter_bridge` | `ros_gz_bridge` | Bridges the topics listed below |

## TF tree

```
odom
└── base_link
    ├── caster      (fixed, xyz -0.2 0 -0.05)
    ├── laser       (fixed, xyz 0.15 0 0.1)
    └── imu_link    (fixed, xyz 0 0 0.07)
```

- `odom -> base_link`: published by the Gazebo DiffDrive plugin on `/tf`
  (`frame_id` `odom`, `child_frame_id` `base_link`), about 50 Hz.
- `base_link -> caster|laser|imu_link`: fixed joints from the URDF, published by
  `robot_state_publisher`.
- `left_wheel` / `right_wheel` (continuous joints at y = +/-0.17) are in the URDF
  but did not appear in a `view_frames` capture. TODO: bridge wheel joint states.
- There is no `map` frame yet (planned for the SLAM/AMCL steps).

## Topics (bridge)

`[` = Gazebo to ROS, `]` = ROS to Gazebo.

| Topic | ROS type | Gazebo type | Direction | Source |
|---|---|---|---|---|
| `/clock` | `rosgraph_msgs/msg/Clock` | `gz.msgs.Clock` | Gz -> ROS | Gazebo sim time |
| `/scan` | `sensor_msgs/msg/LaserScan` | `gz.msgs.LaserScan` | Gz -> ROS | `gpu_lidar`, frame `laser`, 360 samples, 10 Hz, 0.12-10 m |
| `/odom` | `nav_msgs/msg/Odometry` | `gz.msgs.Odometry` | Gz -> ROS | DiffDrive, 50 Hz |
| `/imu` | `sensor_msgs/msg/Imu` | `gz.msgs.IMU` | Gz -> ROS | IMU sensor, frame `imu_link`, 100 Hz |
| `/tf` | `tf2_msgs/msg/TFMessage` | `gz.msgs.Pose_V` | Gz -> ROS | DiffDrive (`odom -> base_link`) |
| `/cmd_vel` | `geometry_msgs/msg/Twist` | `gz.msgs.Twist` | ROS -> Gz | DiffDrive input |

`/robot_description` and `/joint_states` are ROS-side only (not bridged).

## Robot parameters (xacro properties)

Wheel radius 0.1 m, wheel width 0.05 m, wheel separation 0.34 m, caster radius
0.05 m. Body box 0.5 x 0.3 x 0.12 m, mass 8 kg.

## World

`warehouse` world, ODE physics at 1 ms step, 20 x 20 m ground plane, four walls
centred at +/-4 m, and three static boxes (`box1`, `box2`, `box3`).

## Diagram

TODO: add `docs/images/architecture.png`.
