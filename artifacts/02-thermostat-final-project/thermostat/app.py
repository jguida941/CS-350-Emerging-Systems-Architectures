from datetime import datetime
from time import sleep, time
from typing import Optional

from .config import RuntimeConfig
from .controller import (
    ThermostatState,
    apply_button_events,
    determine_led_action,
    record_temperature,
)
from .hardware import (
    ManagedDisplay,
    apply_led_action,
    button_pressed,
    create_buttons,
    create_leds,
    create_sensor,
    create_serial_connection,
    read_temp_f,
)
from .uart import send_uart


def lcd_status_line(show_temp: bool, state: ThermostatState, temp_f: float) -> str:
    if show_temp:
        return f"Temp: {temp_f:.1f}F"

    return f"{state.mode.upper()} Set:{state.set_point}"


def main(config: Optional[RuntimeConfig] = None) -> None:
    config = config or RuntimeConfig()
    print("Starting thermostat...")

    sensor = create_sensor()
    print("AHT20 sensor ready")

    serial_connection = create_serial_connection(config)
    red_led, blue_led = create_leds(config)
    mode_button, up_button, down_button = create_buttons(config)
    screen = ManagedDisplay(
        config.lcd_pins,
        columns=config.lcd_columns,
        rows=config.lcd_rows,
    )

    state = ThermostatState(
        set_point=config.default_set_point,
        last_good_temp_f=float(config.default_set_point),
    )
    last_mode = False
    last_up = False
    last_down = False
    last_uart_time = 0
    last_lcd_update_time = 0
    show_temp = True
    last_led_action = None

    try:
        while True:
            try:
                temp_f = read_temp_f(sensor)
                state = record_temperature(state, temp_f)
            except OSError as exc:
                temp_f = state.last_good_temp_f
                print("AHT20 read error, using last temp:", exc)

            mode_now = button_pressed(mode_button)
            up_now = button_pressed(up_button)
            down_now = button_pressed(down_button)

            mode_edge = mode_now and not last_mode
            up_edge = up_now and not last_up
            down_edge = down_now and not last_down

            previous_state = state
            state = apply_button_events(state, mode_edge, up_edge, down_edge)

            if state.mode != previous_state.mode:
                print("State:", state.mode)
            if state.set_point != previous_state.set_point:
                print("Set point:", state.set_point)

            last_mode = mode_now
            last_up = up_now
            last_down = down_now

            led_action = determine_led_action(state.mode, temp_f, state.set_point)
            if led_action != last_led_action:
                apply_led_action(led_action, red_led, blue_led)
                print("LED action:", led_action)
                last_led_action = led_action

            now = time()

            if now - last_lcd_update_time >= config.lcd_update_seconds:
                line1 = datetime.now().strftime("%m/%d %H:%M")
                line2 = lcd_status_line(show_temp, state, temp_f)
                screen.update(line1, line2)
                print("LCD:", line1, "|", line2)

                show_temp = not show_temp
                last_lcd_update_time = now

            if now - last_uart_time >= config.uart_update_seconds:
                send_uart(serial_connection, state.mode, temp_f, state.set_point)
                last_uart_time = now

            sleep(config.loop_sleep_seconds)

    except KeyboardInterrupt:
        print("Stopping thermostat...")

    finally:
        red_led.off()
        blue_led.off()
        screen.cleanup()

        if serial_connection is not None:
            serial_connection.close()

        print("Cleaned up. Exiting.")
