# MCUSH Python Library

MCUSH project's Python core module and test suite/framework. It simplifies testing work and supports creating CLI/GUI applications.

## Project Background

This project was originally developed by Mr. Peng Shulin. We express our deep respect and gratitude for his contributions.

**Version 1.5.9 and subsequent versions are maintained by the community, committed to the continuous development and improvement of the project.**

## Features

- 🚀 Embedded firmware testing framework
- 📡 Serial communication support
- 🔧 Multiple instrument device integration
- 📊 Data acquisition and analysis
- 🖥️ CLI/GUI application development support

## Installation

```bash
pip install mcush-python
```

## Quick Start

```python
import mcush

# Create MCUSH controller instance
controller = mcush.Mcush('/dev/ttyUSB0')

# Basic operation example
print("LED count:", controller.getLedNumber())
controller.ledOn(0)  # Turn on the first LED
```

## Supported Devices

- Android devices
- Fluke test instruments
- Keysight equipment
- Linkong software
- Rigol instruments
- Uni-Trend devices
- Various miscellaneous devices

## Dependencies

- pyserial >= 3.5
- pymodbus >= 3.11
- paho-mqtt >= 2.1

## License

This project is maintained and distributed under the non-commercial authorization of the original author.

## Contact

- Original Author: Peng Shulin <trees_peng@163.com>
- Current Maintainer: Aaron Yang <3300390005@qq.com>

## Contributing

Welcome to submit Issues and Pull Requests to help improve this project.

## Acknowledgments

Special thanks to Mr. Peng Shulin for his pioneering work on the MCUSH project.

---

*Version 1.5.9 - Community Maintenance Version*