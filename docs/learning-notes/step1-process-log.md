# Step 1 process log: amr_sim

Environment found: ROS_DISTRO=jazzy, Gazebo Sim 8.11.0 (Harmonic). Workspace `~/amr_sim` was empty. Package lives in `~/amr_sim/amr_sim/`.

## 1. Commands, in order

| # | Command | What / why |
|---|---|---|
| 1 | `echo $ROS_DISTRO` | Required first step; picks package/plugin naming. Result: jazzy. |
| 2 | `gz sim --version` | Same. Result: 8.11.0, so Harmonic, so `gz-sim-*-system` plugin names (not `ignition-*`). |
| 3 | `ls /opt/ros` | Confirm installed distro. |
| 4 | `ls -A <workspace>` | Confirm workspace was empty. |
| 5 | `ls /opt/ros/*/share \| grep -E "ros_gz\|ros_ign\|gz"` | Confirm `ros_gz_sim` and `ros_gz_bridge` are installed (they are; no `ros_ign_*`). Nothing needed installing. |
| 6 | `mkdir -p amr_sim/{urdf,worlds,launch}` | Create package skeleton. |
| 7 | `cat > package.xml / CMakeLists.txt / urdf/amr.urdf.xacro` (heredocs) | Write the package files. |
| 8 | `python3 - <<EOF ... EOF` generating `worlds/warehouse.sdf` | Script produced the world file (4 walls + 3 boxes via a helper function) so the repeated model XML was not hand-typed. The script's output file is the artifact; the script itself was not saved. |
| 9 | `cat > launch/sim.launch.py` | Write the launch file. |
| 10 | `source /opt/ros/jazzy/setup.bash && xacro amr_sim/urdf/amr.urdf.xacro > $TMPDIR/a.urdf` | Intended: expand xacro to a file. **Failed**: `$TMPDIR` was empty so the target was `/a.urdf` (permission denied). |
| 11 | `xacro ... > <scratchpad>/a.urdf` | Redo with an explicit writable path. Succeeded. |
| 12 | `gz sdf -p <scratchpad>/a.urdf \| grep -E "gz_frame_id\|sensor name\|joint name"` | Convert URDF to SDF the way Gazebo will, to check sensors, joints and `gz_frame_id` survive. This printed the `gz_frame_id` warnings. |
| 13 | `gz sdf -k amr_sim/worlds/warehouse.sdf` | Validate the world SDF. Result: Valid. |
| 14 | `colcon build --symlink-install` | Build/install the package. |
| 15 | `source install/setup.bash` | Make the package visible to `ros2`. |
| 16 | `ros2 launch amr_sim sim.launch.py headless:=true` (backgrounded, `timeout 40`) **and** a second `ros2 launch amr_sim sim.launch.py` at the same time | First test attempt. Mistakes: `headless:=true` is not an argument the launch file declared, and I started two launches at once. |
| 17 | `ros2 topic list`, `ros2 topic echo /scan --once --field header`, `ros2 topic echo /odom --once --field child_frame_id`, `ros2 topic pub -t 20 /cmd_vel ...`, `ros2 topic echo /odom ...`, `ros2 topic echo /tf --once \| head -12`, `grep -iE "error\|fail" l.log` | Smoke test. Topic list was correct, but the echoes printed nothing (cause not established; see section 4). Log showed the GUI crash. |
| 18 | `pkill -f "gz sim"; sleep 1` followed by a launch with `gz_args:=...` | Meant to clean up stale sims. **`pkill -f` matched my own bash command line** (it contained "gz sim"), killing the shell (exit 144). Also `gz_args` was not a declared launch argument. |
| 19 | `python3` edit of `launch/sim.launch.py` | Added the `gz_flags` launch argument (see section 2) so the sim can run headless. |
| 20 | `colcon build --symlink-install`, `source install/setup.bash` | Rebuild after the launch edit. |
| 21 | `ros2 launch amr_sim sim.launch.py gz_flags:="-s --headless-rendering"` (backgrounded, `timeout 60`, log to scratchpad) | Run server-only, no GUI, to avoid the snap crash. |
| 22 | `ros2 topic echo /scan --once --field header`; `... /odom --once --field child_frame_id`; `ros2 topic pub -t 30 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.3}}" -r 10`; `ros2 topic echo /odom --once --field pose.pose.position`; `ros2 topic echo /tf --once \| head -14`; `ros2 topic echo /imu --once --field header.frame_id`; `grep -iE "error\|fail\|warn" l.log` | Verification. Results: scan frame `laser`; odom child `base_link`; x went to ~1.52 m under 0.3 m/s; `/tf` had `odom` -> `base_link`; imu frame `imu_link`; only the two warning types in section 4. |

Not run: any install (nothing was missing), `rviz2`, `ros2 run tf2_ros tf2_echo` (given to you as a verify command but I did not execute it), GUI mode (crashes).

## 2. Files created or edited

All under `~/amr_sim/amr_sim/` unless noted.

### package.xml
Package metadata, `ament_cmake` build type. Exec deps: `ros_gz_sim`, `ros_gz_bridge`, `robot_state_publisher`, `xacro`, `launch_ros`. License field I set: Apache-2.0 (my choice; change if wrong).

### CMakeLists.txt
Only installs `urdf`, `worlds`, `launch` into `share/amr_sim`, then `ament_package()`. No code is compiled.

### urdf/amr.urdf.xacro
Robot description. Key blocks:
- `xacro:property`: `wheel_r=0.1`, `wheel_w=0.05`, `sep=0.34` (wheel separation), `caster_r=0.05`.
- `xacro:macro box_inertial`: box inertia from mass and dimensions (used by base_link).
- `link base_link`: 0.5 x 0.3 x 0.12 m box, mass 8 kg, visual + collision. Origin is at axle height.
- `xacro:macro wheel` (called for `left` y=+0.17 and `right` y=-0.17): cylinder link rotated 90 deg about x, mass 1 kg; joint `<name>_wheel_joint`, type `continuous`, axis `0 1 0`, parent `base_link`.
- `link caster` + `caster_joint` (fixed): sphere r=0.05 at x=-0.2, z=-0.05 (so its bottom is at ground level with the wheels). Collision has `<surface><friction><ode><mu>0</mu><mu2>0</mu2>`, so zero friction.
- `link laser` + `laser_joint` (fixed): small cylinder at x=0.15, z=0.1.
- `link imu_link` + `imu_joint` (fixed): massless-ish marker (0.01 kg) at z=0.07.
- `<gazebo>` DiffDrive plugin (`filename="gz-sim-diff-drive-system" name="gz::sim::systems::DiffDrive"`):
  - `left_joint` / `right_joint`: which joints it drives.
  - `wheel_separation`, `wheel_radius`: kinematics for odometry and cmd_vel conversion; must match the geometry above.
  - `topic` `/cmd_vel`: Gazebo-side input topic.
  - `odom_topic` `/odom`: Gazebo-side odometry output.
  - `tf_topic` `/tf`: Gazebo-side topic for the odom->base_link pose.
  - `frame_id` `odom`, `child_frame_id` `base_link`: names in the odometry message and TF.
  - `odom_publish_frequency` 50 Hz.
- `<gazebo reference="laser">` sensor `laser`, `type="gpu_lidar"`:
  - `gz_frame_id` `laser`: frame_id placed in output messages.
  - `topic` `/scan`, `update_rate` 10, `always_on` true.
  - `lidar/scan/horizontal`: 360 samples, -3.14159 to 3.14159 rad (full circle).
  - `lidar/range`: min 0.12, max 10.0 m.
- `<gazebo reference="imu_link">` sensor `imu`, `type="imu"`: `gz_frame_id` `imu_link`, `topic` `/imu`, 100 Hz, always_on. No noise model configured.

### worlds/warehouse.sdf
SDF 1.9, world name `warehouse`. Key blocks:
- `physics` (type `ode`, `max_step_size` 0.001, `real_time_factor` 1.0).
- World system plugins: `gz-sim-physics-system` (dynamics), `gz-sim-user-commands-system` (entity create/spawn requests, needed for `create`), `gz-sim-scene-broadcaster-system` (feeds the GUI), `gz-sim-sensors-system` with `<render_engine>ogre2</render_engine>` (runs the lidar), `gz-sim-imu-system` (runs the IMU).
- `light` named `sun` (directional).
- `model ground`: static plane 20 x 20, collision + visual.
- Walls `wall_n/s/e/w`: static boxes, 1.0 m tall, 0.2 m thick, forming an inner 8 x 8 m room (centres at +-4 m).
- Obstacles `box1` (0.5x0.5x0.5 at 2,1.5), `box2` (0.4x0.8x0.4 at -2,-1), `box3` (0.3x0.3x1.0 at 1,-2.5): static boxes.

### launch/sim.launch.py
Key blocks:
- `xacro.process_file(...).toxml()`: expands the xacro to a URDF string at launch time.
- `DeclareLaunchArgument('gz_flags', default '')`: extra `gz sim` flags (added in step 19).
- `IncludeLaunchDescription` of `ros_gz_sim`'s `gz_sim.launch.py`, with `gz_args` = `-r <flags> <world path>`. `-r` starts the sim running immediately.
- `robot_state_publisher` node: `robot_description` param, `use_sim_time: True`. Publishes the URDF on `/robot_description` and fixed-joint transforms on `/tf_static`.
- `ros_gz_sim create` node: `-topic robot_description -name amr -x 0 -y 0 -z 0.15`. Spawns the robot from the topic into the running world.
- `ros_gz_bridge parameter_bridge` node with arguments (`topic@ROS_type<dir>GZ_type`):
  - `/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock` (`[` = Gazebo to ROS)
  - `/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan` (Gazebo to ROS)
  - `/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry` (Gazebo to ROS)
  - `/imu@sensor_msgs/msg/Imu[gz.msgs.IMU` (Gazebo to ROS)
  - `/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V` (Gazebo to ROS)
  - `/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist` (`]` = ROS to Gazebo)

### Build outputs
`~/amr_sim/build/`, `install/`, `log/` created by colcon. Scratch file `a.urdf` is in the session scratchpad, not the project.

### This file
`~/amr_sim/step1-process-log.md`.

## 3. Design decisions made without asking

| Decision | Chosen | Rejected alternative | Reason |
|---|---|---|---|
| Caster | Fixed sphere joint with mu=0 | Free-rotating ball caster (extra joints) or a real friction-model caster | Minimal; zero friction makes it behave like a ball without extra joints. Caveat: a fixed sphere is not a real caster; fine for flat-floor sim. |
| Lidar | 360 samples, full 2pi, 10 Hz, range 0.12-10 m | Narrower FOV, higher rate/resolution | Common default for a generic 2D scan; cheap. All numbers are my guesses, not from a spec. |
| Lidar type | `gpu_lidar` | `lidar` (CPU) | Standard in Harmonic examples. Requires the Sensors system with ogre2. |
| IMU | 100 Hz, no noise | Add noise model | Minimal; noise can be added later. |
| Room | 8 x 8 m, 1 m walls | Larger warehouse with shelves | "Keep it minimal". |
| Obstacles | 3 static boxes, hand-placed | Dynamic boxes, random placement | Static avoids physics clutter; positions arbitrary. |
| Dimensions/mass | base 0.5x0.3x0.12 / 8 kg, wheel r=0.1, separation 0.34, wheel 1 kg | Other sizes | Plausible small AMR; arbitrary. |
| base_link origin | At axle height (spawn z=0.15) | Origin at ground (REP-120 base_footprint style) | Simpler: odom child frame is `base_link` as requested, no extra footprint link. Spawn z=0.15 drops the robot slightly. |
| Caster/body geometry | caster at x=-0.2 behind, sphere bottom level with wheel bottoms | Front caster | Arbitrary; either balances. |
| Physics | ODE, 1 ms step | Default dartsim | Not strongly justified; I chose ODE explicitly and did not test against dartsim. Unsure which is the Harmonic default. |
| Wheel joints | `continuous` | `revolute` with limits | Wheels spin freely. (`gz sdf` converted them to `revolute`; worked in practice.) |
| Diff-drive topics | Global names `/cmd_vel`, `/odom`, `/tf` on the Gazebo side | Default model-scoped topics (`/model/amr/cmd_vel`) | So the bridge uses the same names as ROS. |
| `/tf` | Gazebo to ROS only | Bidirectional | Only the diff-drive plugin publishes it; ROS has no reason to send poses back. `robot_state_publisher` publishes `/tf_static` separately. |
| `/cmd_vel` | ROS to Gazebo only | Bidirectional | Command flows one way. |
| Sensor/clock bridges | Gazebo to ROS only | Bidirectional | Same. |
| Frame names | `laser`, `imu_link` via `gz_frame_id` | Leave Gazebo's default scoped frame names | Request required frame `laser`; scoped names would not match URDF frames. |
| Spawning | `ros_gz_sim create -topic robot_description` | `-file` of a pre-generated URDF/SDF | Keeps one source of truth (xacro) and reuses the robot_state_publisher string. |
| `use_sim_time` | Set only on robot_state_publisher | Global parameter | Only one ROS node besides the bridge; no other nodes exist. Not set on the bridge (not needed). |
| `gz_flags` launch arg | Added | Leave GUI-only | Needed to test headless because the GUI crashes here. Not in your original spec. |
| Package type | `ament_cmake` data-only | `ament_python` | No Python code to install beyond launch files. |
| Not added | `/joint_states` bridge, ros2_control, RViz config, README, tests, wheel TFs | Included | "Keep it minimal". Consequence: wheel links have no TF frames in ROS (no joint state source). `/joint_states` showed in `ros2 topic list` only because `robot_state_publisher` subscribes to it. |
| License | Apache-2.0 | Other | Guess; change it. |

## 4. Problems and resolutions

1. **`$TMPDIR` empty, write to `/a.urdf` denied.** Used an explicit scratchpad path. Cause: env var unset in this shell.
2. **First smoke test printed no echo output.** Topics were listed correctly, so the bridge and sim were up, but `echo --once` results were empty. Cause not established. Candidates: two simultaneous launches, the sim not past startup, or the 5 s echo timeouts. Not investigated further because the clean rerun worked.
3. **`headless:=true` / `gz_args:=` passed to a launch file that did not declare them.** Wrong assumption on my part. Fixed by declaring `gz_flags` and using that.
4. **`pkill -f "gz sim"` killed my own shell (exit 144).** The pattern matched the command string itself. Not repeated. Stale sim processes from the earlier timed launch were left to expire via `timeout`; I did not verify they had exited before the second run.
5. **Snap `libpthread` crash in the GUI:** `gz sim gui: symbol lookup error: /snap/core20/current/lib/x86_64-linux-gnu/libpthread.so.0: undefined symbol: __libc_pthread_init, version GLIBC_PRIVATE`. Seen in the log of the GUI launch. Left unresolved: it is an environment problem (a snap runtime's libs leaking into the GUI process), not a package problem. Workaround used: server-only mode (`-s --headless-rendering`). I did not diagnose which variable (`LD_LIBRARY_PATH`, etc.) causes it. **Unconfirmed guess**: it comes from a snap-installed app (e.g. VS Code) environment.
6. **`gz_frame_id` warning** (`XML Element[gz_frame_id], child of element[sensor], not defined in SDF. Copying ...`). Left in place. The conversion copies the element through, and the echoed frame ids (`laser`, `imu_link`) show it takes effect. Unsure whether this is the officially recommended way for URDF-sourced sensors vs. defining the sensor in SDF.
7. **`robot_state_publisher` / kdl_parser warning:** root link `base_link` has an inertia, which KDL does not support on a root link. Left in place; the tree still publishes. The warning's own suggested fix is a dummy root link (e.g. `base_footprint`), which I did not add because it would change the frame tree you specified.
8. **`continuous` joints converted to `revolute` in `gz sdf -p` output.** Observed, not investigated. Motion worked.

## 5. What to search

Keywords, not URLs. Items marked (?) mean I am unsure the exact page or option name exists as written.

**Environment and versions**
- ROS 2 Jazzy docs: "Gazebo Harmonic" and "ros_gz" compatibility / "Using ROS 2 with Gazebo". (?) exact page title
- Gazebo Harmonic docs: "ROS 2 integration", "Gazebo and ROS installation".
- Jazzy ships Harmonic pairing: search "ROS and Gazebo version pairings".

**ros_gz packages**
- `ros_gz_bridge` README: "parameter_bridge", bridge argument syntax `@ [ ]`, the table of supported message pairs (LaserScan, Odometry, Imu, Clock, Pose_V/TFMessage, Twist).
- `ros_gz_sim` README: "create" node (`-topic`, `-name`, `-x -y -z`), `gz_sim.launch.py` and its `gz_args` argument.
- (?) whether Jazzy's bridge also supports YAML config (`--ros-args -p config_file:=`): I used the argument form only.

**Gazebo Harmonic systems and sensors**
- "DiffDrive" system, gz-sim API docs: `gz::sim::systems::DiffDrive`, params `left_joint`, `right_joint`, `wheel_separation`, `wheel_radius`, `odom_publish_frequency`, `frame_id`, `child_frame_id`, `tf_topic`, `odom_topic`, `topic`.
- Tutorial: "Move a robot" (Gazebo Sim tutorials), "Sensors" tutorial, "Spawn URDF" tutorial.
- "gpu_lidar sensor" / "Lidar sensor" in gz-sensors docs; SDF `<lidar>`: `<scan>`, `<horizontal>`, `<samples>`, `<range>`.
- "IMU sensor", gz-sim `Imu` system; SDF `<imu>` noise options.
- "Sensors system", `render_engine` (ogre2), headless rendering (`--headless-rendering`).
- "UserCommands system", "SceneBroadcaster system", "Physics system".
- `gz sim` command-line flags: `-r`, `-s`, `-g`, `--headless-rendering`, `-v`.
- `gz sdf` tool: `-p` (print/convert), `-k` (check).

**SDF and URDF**
- SDFormat spec: `<world>`, `<model>`, `<static>`, `<plane>`, `<surface><friction><ode><mu>`, `<physics>`, `<light>`.
- SDFormat "Using URDF in Gazebo": `<gazebo>` extension tags, `<gazebo reference="...">`, fixed-joint lumping, `<sensor>` in URDF, `gz_frame_id`. (?) whether `gz_frame_id` is documented there or only in sensor docs / forum answers.
- URDF wiki: `link`, `joint` types (`continuous`, `fixed`), `inertial`, `xacro` (properties, macros, `${}` expressions).
- "Moment of inertia of a solid cuboid / cylinder / sphere" (formulas I used).

**ROS 2**
- REP-103 "Standard Units of Measure and Coordinate Conventions" (x forward, y left, z up; radians; SI).
- REP-105 "Coordinate Frames for Mobile Platforms" (`odom`, `base_link`, `map`; who publishes odom -> base_link).
- (?) REP-120 "Coordinate Frames for Humanoid Robots" mentioned only because of `base_footprint`; I am not sure that REP is the right source for `base_footprint`. Check REP-105 first.
- `robot_state_publisher` docs: `/tf_static`, `/joint_states`, `robot_description` param, KDL root-inertia warning (search the warning text).
- `use_sim_time` and `/clock` in ROS 2 ("Using simulated time" / "About Clock and Time" design article).
- `tf2_ros` `tf2_echo`, `view_frames`.
- Launch: "Creating launch files" tutorial, `IncludeLaunchDescription`, `DeclareLaunchArgument`, `LaunchConfiguration`, `PythonLaunchDescriptionSource`.
- `ament_cmake` packaging: "Creating a package" tutorial, `install(DIRECTORY ...)`.
- `ros2 topic echo --field`, `--once`; `ros2 topic pub -r`.

**Environment issue**
- Search: `symbol lookup error snap libpthread __libc_pthread_init GLIBC_PRIVATE`; related keywords "VS Code snap" "LD_LIBRARY_PATH" "gz sim gui". (?) I have not confirmed the cause.
