# BK Precision 1900 Series Control

A lightweight Python 3.12 library and CLI for controlling **BK Precision 1900-series programmable DC power supplies**, tested on the **BK 1902B**.
It provides both a **Pythonic context-manager interface** and a simple **command-line tool** for automation or lab use.

## ✨ Features

- Safe open/close via context manager
- Set and read output voltage/current
- Enable or disable output
- Query front-panel readings (voltage, current, CV/CC mode)
- Command-line interface (`bk1902b`) for quick manual control

## 🧰 Installation

### From PyPI

```bash
pip install bk_precision_1900
```

### From Source

```bash
git clone https://github.com/DephyInc/bk_precision_1900.git
cd bk_precision_1900
pip install -e ".[dev]"
```

## 🚀 Command-Line Usage

After installation, a console script `bk1902b` is available.

```bash
# Set output voltage to 12.0 V
bk1902b set-voltage --port /dev/ttyUSB0 12.0

# Set output current to 2.0 A
bk1902b set-current --port /dev/ttyUSB0 2.0

# Turn output on / off
bk1902b output --port /dev/ttyUSB0 on
bk1902b output --port /dev/ttyUSB0 off

# Read front-panel display (voltage, current, mode)
bk1902b read-display --port /dev/ttyUSB0
bk1902b read-display --port /dev/ttyUSB0 --json
```

> Replace `/dev/ttyUSB0` with your serial port (e.g., `COM3` on Windows).

## 🧑‍💻 Library Usage

```bash
import time
from bk_precision_1900.bk1902b import BK1902B

with BK1902B("/dev/ttyUSB0") as psu:
    psu.set_current(0.1)
    psu.set_voltage(5.0)
    psu.enable_output()
    time.sleep(5)
    psu.disable_output()
```

## 🧩 Demo Script

A minimal example (`bk_precision_1900/bk_demo.py`) is included:

```bash
python -m bk_precision_1900.bk_demo /dev/ttyUSB0
```

It cycles voltages between 1 V and 40 V, reads back live measurements, and prints CV/CC status.

## 🧪 Development

```bash
    # Format, lint, and type-check
    ruff format .
    ruff check .
    mypy .
```

Requirements are managed via `pyproject.toml` and use [Ruff](https://docs.astral.sh/ruff) for linting + formatting and [Mypy](https://mypy-lang.org) for static type checking.

## 📝 To Do

- Implement full BK 1900 command set (`GETS`, `SOVP`, `SOCP`, etc.)
- Query limits instead of hard-coding max values
- Add unit tests / mock serial backend
- Automate releases (e.g. GitHub Actions)

## ⚖️ License

MIT License © Dephy Inc.
See [https://dephyinc.mit-license.org/](LICENSE) for details.
