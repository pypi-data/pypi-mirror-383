# LeRobot + teleop Integration

## Getting Started

```bash
pip install lerobot_teleoperator_violin

lerobot-teleoperate \
    --robot.type=lerobot_robot_viola \
    --robot.port=/dev/ttyUSB1 \
    --robot.id=my_awesome_staraiviola_arm \
    --teleop.type=lerobot_teleoperator_violin \
    --teleop.port=/dev/ttyUSB0 \
    --teleop.id=my_awesome_staraiviolin_arm
    
```

## Development

Install the package in editable mode:

```bash
git clone https://github.com/servodevelop/fashionstar-lerobot-teleoperator-violin.git
cd lerobot_teleoperator_violin
pip install -e .
```
