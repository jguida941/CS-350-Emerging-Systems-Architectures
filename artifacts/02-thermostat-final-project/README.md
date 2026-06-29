# Raspberry Pi Smart Thermostat

CS-350 Raspberry Pi smart thermostat project. The app reads temperature from an AHT20 sensor, cycles between `OFF`, `HEAT`, and `COOL`, updates a 16x2 LCD, drives red and blue PWM LEDs, and emits UART status messages.

## Project Structure

```text
.
├── Thermostat.py                  # Backward-compatible entrypoint
├── thermostat/                    # Modular thermostat package
│   ├── app.py                     # Main runtime loop
│   ├── config.py                  # Pins, timing, and UART settings
│   ├── controller.py              # Pure thermostat state and LED logic
│   ├── hardware.py                # Raspberry Pi, LCD, sensor, button, and LED adapters
│   └── uart.py                    # UART message formatting and sending
├── docs/
│   ├── CS350_Thermostat_State_Machine.md
│   └── CS350_Thermostat_State_Machine.pdf
└── tests/
    └── test_controller.py
```

## Hardware

- Raspberry Pi with GPIO access
- AHT20 temperature sensor over I2C
- 16x2 character LCD
- Red and blue PWM LEDs
- Three buttons for mode, set point up, and set point down
- UART on `/dev/ttyS0` at `115200` baud

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

Enable I2C and UART on the Raspberry Pi before running the app.

## Run

```bash
python3 Thermostat.py
```

You can also run the package directly:

```bash
python3 -m thermostat
```

## Behavior

- Mode button cycles `OFF -> HEAT -> COOL -> OFF`.
- Up and down buttons adjust the set point by 1 degree.
- LCD alternates between current temperature and mode/set point.
- UART emits `state,current_temperature,set_point`.
- In `HEAT`, the red LED fades when temperature is below set point and stays solid once the target is reached.
- In `COOL`, the blue LED fades when temperature is above set point and stays solid once the target is reached.

The state-machine documentation is available in [docs/CS350_Thermostat_State_Machine.md](docs/CS350_Thermostat_State_Machine.md).

## Validate

```bash
python3 -m unittest discover -s tests
python3 -m compileall Thermostat.py thermostat tests
```
