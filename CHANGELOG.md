# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-06

### Added
- ROS 2 package `amr_sim` (ament_cmake, Apache-2.0).
- Differential-drive robot description (`urdf/amr.urdf.xacro`): `base_link`,
  left/right wheels, caster, `laser` and `imu_link`.
- Gazebo Harmonic DiffDrive plugin publishing odometry at 50 Hz.
- `gpu_lidar` sensor on `/scan` (360 samples, 10 Hz, 0.12-10 m) and IMU on
  `/imu` (100 Hz).
- `worlds/warehouse.sdf`: walled room (about 8 m x 8 m) with three box obstacles.
- `launch/sim.launch.py`: starts Gazebo, `robot_state_publisher`, spawns the
  robot and runs `ros_gz_bridge` for `/clock`, `/scan`, `/odom`, `/imu`, `/tf`
  and `/cmd_vel`.
- Launch argument `gz_flags` to pass extra `gz sim` flags (e.g. `-s` for headless).

[Unreleased]: https://github.com/AswinprabhuM/amr-nav-sim/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/AswinprabhuM/amr-nav-sim/releases/tag/v0.1.0
