# CS-350 Emerging Systems Architectures & Technologies: Module Eight Journal

**Justin Guida**
CS-350-14294-M01 | Emerging Systems Architectures & Technologies | 2026 C-3 (May – Jun)
Southern New Hampshire University

---

## Artifacts in this repository

| # | Artifact | Course deliverable | Location |
|---|----------|--------------------|----------|
| 1 | **Morse Code Button/LED State Machine** | 5-1 Milestone Three: Input With Buttons Lab | [`artifacts/01-milestone-three-buttons-lab/`](artifacts/01-milestone-three-buttons-lab/) |
| 2 | **Raspberry Pi Smart Thermostat** | 7-1 Final Project | [`artifacts/02-thermostat-final-project/`](artifacts/02-thermostat-final-project/) |

---

## Project Summaries: What problem was each solving?

**Artifact 1: Input With Buttons Lab (Milestone Three).** This milestone asked me to drive
hardware from software on a Raspberry Pi: blink red and blue LEDs to transmit a message in Morse
code, show status on a 16x2 LCD, and toggle the transmitted message between **SOS** and **OK** when a
button is pressed. The real problem it solved was learning to model timed, event-driven hardware
behavior as a **finite state machine** (`off → dot → dash → dotDashPause → letterPause →
wordPause`) with strict timing (500 ms dots, 1500 ms dashes, and the 250/750/3000 ms pauses
between symbols, letters, and words) while still responding to asynchronous button input on a
separate thread.

**Artifact 2: Smart Thermostat (Final Project).** The final project simulated a real embedded
product: a thermostat that reads temperature from an **AHT20 sensor over I2C**, lets the user cycle
modes and adjust a set point with three buttons, shows state on the LCD, drives red/blue **PWM LEDs**
to indicate heating/cooling effort, and reports status to a server over **UART** as
`state,current_temperature,set_point`. The core problem was the same kind of problem real
connected devices solve: take noisy sensor input, run it through a deterministic control loop
(`OFF → HEAT → COOL`), and produce both human-facing output (LCD/LEDs) and machine-facing output
(UART), all on constrained hardware.

## What did I do particularly well?

I'm most proud of how cleanly I separated **control logic from hardware** in the thermostat. The
decision-making lives in [`controller.py`](artifacts/02-thermostat-final-project/thermostat/controller.py)
as small **pure functions** over an immutable `@dataclass(frozen=True)` `ThermostatState`
(`apply_button_events`, `record_temperature`, `determine_led_action`). Because that logic never
touches a GPIO pin directly, I could prove it correct with ordinary unit tests
([`tests/test_controller.py`](artifacts/02-thermostat-final-project/tests/test_controller.py)) on
my laptop without any Raspberry Pi attached. In the buttons lab I did the timing-critical Morse
state machine well, getting the symbol/letter/word pauses right and keeping the button responsive
by running the transmission on its own thread.

## Where could I improve?

In the Milestone Three code, hardware objects (LEDs, the LCD, GPIO pins) are created at module/class
scope, which makes that artifact harder to unit-test than the final project, since it assumes the real
board is present. If I revisited it, I'd apply the same lesson the thermostat taught me: push the
hardware behind a thin adapter and keep the state-machine logic pure. I'd also add more defensive
handling around I2C reads (transient sensor errors) and replace remaining `sleep`-based timing with
a more precise scheduler so long-running transmissions don't drift.

## Tools and resources I'm adding to my support network

- **`python-statemachine` and `gpiozero`/`adafruit-blinka`** libraries for modeling embedded
  behavior and talking to GPIO, I2C, and character LCDs.
- **The state-machine diagram workflow** (Mermaid + a design doc, see
  [`docs/CS350_Thermostat_State_Machine.md`](artifacts/02-thermostat-final-project/docs/CS350_Thermostat_State_Machine.md))
  so the design is documented *before* and alongside the code.
- **`unittest` and `compileall`** as a lightweight validation gate I can run before every commit.
- Vendor and community references such as Raspberry Pi GPIO docs, Adafruit CircuitPython guides, and
  the AHT20 datasheet, which I'll keep relying on for future hardware projects.

## Transferable skills

The biggest transferable skill is **modeling a problem as a finite state machine** and keeping the
"what to do" (pure logic) separate from the "how to do it" (I/O and hardware). That separation, plus
**writing unit tests against the logic layer**, applies to almost any software, not just embedded.
I'm also taking away comfort with **communication protocols** (I2C, UART, GPIO/PWM) and reading
hardware against requirements, which transfers directly to IoT, robotics, and any
hardware-adjacent work.

## How I made the work maintainable, readable, and adaptable

- **Maintainable:** The thermostat is a real Python package split by responsibility:
  [`config.py`](artifacts/02-thermostat-final-project/thermostat/config.py) (pins/timing/UART
  settings), [`controller.py`](artifacts/02-thermostat-final-project/thermostat/controller.py)
  (pure logic), [`hardware.py`](artifacts/02-thermostat-final-project/thermostat/hardware.py)
  (device adapters), [`uart.py`](artifacts/02-thermostat-final-project/thermostat/uart.py)
  (messaging), and [`app.py`](artifacts/02-thermostat-final-project/thermostat/app.py) (the runtime
  loop). Unit tests guard the logic so changes are safe.
- **Readable:** Type hints (`Mode`, `LedAction` literals), an immutable state object, descriptive
  function names, consistent comments, and a documented state diagram make intent obvious.
- **Adaptable:** Because pins, timing, and the set point default live in `config.py`, the board can
  be rewired or retuned without touching logic. The hardware adapter boundary means a different
  sensor or display could be dropped in by changing one module, and new modes would be a small,
  localized change to the controller. A backward-compatible `Thermostat.py` entry point keeps the
  original run command working even after the refactor into a package.

---

*This README serves as my Module Eight Journal reflection and as the landing page for the two
CS-350 artifacts archived in this repository.*
