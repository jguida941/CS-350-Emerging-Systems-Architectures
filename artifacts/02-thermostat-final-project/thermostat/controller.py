from dataclasses import dataclass, replace
from math import floor
from typing import Literal

from .config import DEFAULT_SET_POINT

Mode = Literal["off", "heat", "cool"]
LedAction = Literal["off", "heat_fade", "heat_solid", "cool_fade", "cool_solid"]

MODES: tuple[Mode, ...] = ("off", "heat", "cool")


@dataclass(frozen=True)
class ThermostatState:
    mode: Mode = "off"
    set_point: int = DEFAULT_SET_POINT
    last_good_temp_f: float = float(DEFAULT_SET_POINT)


def c_to_f(temp_c: float) -> float:
    return (temp_c * 9 / 5) + 32


def next_mode(mode: Mode) -> Mode:
    try:
        index = MODES.index(mode)
    except ValueError as exc:
        raise ValueError(f"Unknown thermostat mode: {mode}") from exc

    return MODES[(index + 1) % len(MODES)]


def apply_button_events(
    state: ThermostatState,
    mode_pressed: bool,
    up_pressed: bool,
    down_pressed: bool,
) -> ThermostatState:
    mode = next_mode(state.mode) if mode_pressed else state.mode
    set_point = state.set_point

    if up_pressed:
        set_point += 1
    if down_pressed:
        set_point -= 1

    return replace(state, mode=mode, set_point=set_point)


def record_temperature(state: ThermostatState, temp_f: float) -> ThermostatState:
    return replace(state, last_good_temp_f=temp_f)


def determine_led_action(mode: Mode, temp_f: float, set_point: int) -> LedAction:
    if mode == "off":
        return "off"

    if mode == "heat":
        return "heat_fade" if floor(temp_f) < set_point else "heat_solid"

    if mode == "cool":
        return "cool_fade" if floor(temp_f) > set_point else "cool_solid"

    raise ValueError(f"Unknown thermostat mode: {mode}")
