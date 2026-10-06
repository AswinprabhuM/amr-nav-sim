# amr-nav-sim

A ROS 2 Jazzy simulation of a differential-drive autonomous mobile robot (AMR) in
Gazebo Harmonic. The `amr_sim` package provides the robot description, a walled
warehouse world with box obstacles, and a launch file that starts the simulator and
bridges lidar, IMU, odometry, TF and velocity commands to ROS 2. It is the
baseline for SLAM, localization and navigation work (see the roadmap).

<!-- TODO: demo GIF, e.g. docs/images/demo.gif -->
![demo placeholder](docs/images/demo.gif)

## Quick start

Requires ROS 2 Jazzy and Gazebo Harmonic (see [docs/setup.md](docs/setup.md)).

```bash
source /opt/ros/jazzy/setup.bash
colcon build
source install/setup.bash
ros2 launch amr_sim sim.launch.py
```

Verification commands: [docs/verification.md](docs/verification.md).

## Repository layout

```
src/amr_sim/      ROS 2 package
  config/         parameters (empty so far)
  launch/         sim.launch.py
  maps/           saved maps (empty so far)
  rviz/           RViz configs (empty so far)
  test/           tests (empty so far)
  urdf/           amr.urdf.xacro
  worlds/         warehouse.sdf
docs/             architecture, setup, verification, roadmap
scripts/          helper scripts
```

## Status

- [x] Step 1: simulation baseline (robot, world, bridge)
- [ ] Step 2: SLAM Toolbox mapping
- [ ] Step 3: AMCL localization
- [ ] Step 4: Nav2 navigation
- [ ] Step 5: perception (problem to be chosen)

See [docs/roadmap.md](docs/roadmap.md) and [CHANGELOG.md](CHANGELOG.md).

## License

Apache-2.0, see [LICENSE](LICENSE).
