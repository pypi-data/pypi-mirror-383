# LeRobot + teleop Integration

## Getting Started

```bash
pip install lerobot_robot_bimanual_follower

lerobot-teleoperate \
    --robot.type=lerobot_robot_bimanual_follower \
    --robot.arm_name=starai_viola \
    --robot.left_arm_port=/dev/ttyUSB1 \
    --robot.right_arm_port=/dev/ttyUSB3 \
    --robot.id=bi_starai_viola_follower \
    --teleop.type=lerobot_teleoperator_bimanual_leader \
    --teleop.left_arm_port=/dev/ttyUSB0 \
    --teleop.right_arm_port=/dev/ttyUSB2 \
    --teleop.id=bi_starai_leader
```

## Development

Install the package in editable mode:

```bash
git clone https://github.com/servodevelop/fashionstar-lerobot-robot-bimanual-follower.git
cd fashionstar-lerobot-robot-bimanual-follower
pip install -e .
```
