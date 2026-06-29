import unittest

from thermostat.controller import (
    ThermostatState,
    apply_button_events,
    c_to_f,
    determine_led_action,
    next_mode,
)
from thermostat.uart import format_uart_message


class ControllerTests(unittest.TestCase):
    def test_celsius_to_fahrenheit(self):
        self.assertEqual(c_to_f(0), 32)
        self.assertEqual(c_to_f(100), 212)

    def test_mode_cycles_in_required_order(self):
        self.assertEqual(next_mode("off"), "heat")
        self.assertEqual(next_mode("heat"), "cool")
        self.assertEqual(next_mode("cool"), "off")

    def test_button_events_update_state(self):
        state = ThermostatState(mode="off", set_point=72)

        state = apply_button_events(
            state,
            mode_pressed=True,
            up_pressed=True,
            down_pressed=False,
        )

        self.assertEqual(state.mode, "heat")
        self.assertEqual(state.set_point, 73)

    def test_heat_led_actions(self):
        self.assertEqual(determine_led_action("heat", 71.9, 72), "heat_fade")
        self.assertEqual(determine_led_action("heat", 72.0, 72), "heat_solid")

    def test_cool_led_actions(self):
        self.assertEqual(determine_led_action("cool", 72.1, 72), "cool_solid")
        self.assertEqual(determine_led_action("cool", 73.0, 72), "cool_fade")

    def test_uart_format(self):
        self.assertEqual(format_uart_message("heat", 72.25, 73), "heat,72.2,73\n")


if __name__ == "__main__":
    unittest.main()
