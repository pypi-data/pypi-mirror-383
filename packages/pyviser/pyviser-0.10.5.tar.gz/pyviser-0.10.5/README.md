# PyViser

[![forthebadge](https://forthebadge.com/images/badges/made-with-rust.svg)](https://forthebadge.com)

A pip-installable version of [VirxEC/rlviser](https://github.com/VirxEC/rlviser) with minor modifications to facilitate the build process.

## Purpose

The goal of this repository is to provide pre-built pip-installable wheels to PyPI for easy installation of RLViser. For the original code or most up-to-date developments, please see [VirxEC's repository](https://github.com/VirxEC/rlviser).

## Installation

```bash
pip install pyviser
```

### Platform Support

**Currently only macOS (Apple Silicon/ARM64) is supported via pip install.**

Windows and Linux support is in development. If you're interested in helping get these platforms working, contributions are very welcome! Please see the [GitHub repository](https://github.com/2ToTheNthPower/rlviser) for more information.

For other platforms, you can build from source by cloning the repository and using `maturin build --release`.

## About RLViser

RLViser is a lightweight visualizer for [rocketsim-rs](https://github.com/VirxEC/rocketsim-rs) binds that listens for UDP packets.

Any language can communicate with the visualizer by sending UDP packets in the correct format, but `rocketsim-rs` has a `GameState.to_bytes()` function that does this automatically.

![image](https://github.com/VirxEC/rlviser/assets/35614515/47613661-754a-4549-bcef-13df399645be)

### Usage

To see an example of how to communicate with the visualizer, see the [example](https://github.com/VirxEC/rocketsim-rs/blob/master/examples/rlviser_socket.rs) in the [rocketsim-rs](https://github.com/VirxEC/rocketsim-rs) repository.

You can also choose to use the integrated support in [RLGym 2.0](https://github.com/lucas-emery/rocket-league-gym) and [RLGym-PPO](https://github.com/AechPro/rlgym-ppo) or use the [RLViser-Py](https://pypi.org/project/rlviser-py/) library to interface directly from Python via [RocketSim](https://pypi.org/project/RocketSim/) classes.

### Controls

**NOTICE:** These controls WON'T WORK until you've toggled the menu off. The menu is open by default upon launch.

| Key | Action |
| --- | --- |
| `Esc` | Toggle menu |
| `1` - `8` | Change car camera focus |
| `9` | Director camera |
| `0` | Free camera |
| `W` | Move forward |
| `A` | Move left |
| `S` | Move backward |
| `D` | Move right |
| `Space` | Move up |
| `Left Ctrl` | Move down |
| `Left Shift` | Slow |
| `R` | State set ball towards goal |
| `P` | Toggle pause/play |
| `+` | Increase game speed +0.5x |
| `-` | Decrease game speed -0.5x |
| `=` | Set game speed to 1x |
| `Left click`<sup>1</sup> | Drag cars and ball |

<sup>1</sup> - Requires the menu toggled ON to free the cursor, you can drag cars and the ball to move them in the world. Requires the agent on the other side to support state setting.

## Modes

Currently, both standard soccer and hoops are supported.

![image](https://github.com/VirxEC/rlviser/assets/35614515/d804d7e5-b78e-4a0a-9133-38e5aed0681d)

## Credits

All credit for the original RLViser goes to [VirxEC](https://github.com/VirxEC). This repository simply provides pip-installable builds of their excellent work.