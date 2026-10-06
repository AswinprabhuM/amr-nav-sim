# Verification

Run with the simulation launched and the workspace sourced.

| Check | Command | Expected |
|---|---|---|
| Topics exist | `ros2 topic list -t` | `/clock`, `/cmd_vel`, `/imu`, `/odom`, `/scan`, `/tf`, `/robot_description` |
| Lidar publishes | `ros2 topic echo /scan --once --field ranges` | array of 360 floats |
| Odometry rate | `ros2 topic hz /odom` | average rate about 50 Hz |
| Odom TF | `ros2 run tf2_ros tf2_echo odom base_link` | transform printed (zero at rest) |
| TF tree | `ros2 run tf2_tools view_frames` | `odom -> base_link -> {caster, imu_link, laser}` |

Observed on 2026-10-06 (headless launch, `gz_flags:="-s --headless-rendering"`): all
topics above present, `/scan` returned ranges, `/odom` at 50.000 Hz, `odom -> base_link`
resolved.

Known warnings at launch (not errors):
- `kdl_parser`: root link `base_link` has an inertia, which KDL does not support.
- Gazebo: `gz_frame_id` is not defined in SDF for the sensors; it is copied as-is.

TODO: check that driving `/cmd_vel` moves `odom`.
