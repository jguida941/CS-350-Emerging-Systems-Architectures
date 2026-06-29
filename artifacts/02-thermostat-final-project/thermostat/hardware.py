from time import sleep

from .config import LcdPinConfig, RuntimeConfig
from .controller import LedAction, c_to_f


class ManagedDisplay:
    def __init__(
        self,
        lcd_pins: LcdPinConfig,
        columns: int,
        rows: int,
    ) -> None:
        import board
        import digitalio
        import adafruit_character_lcd.character_lcd as characterlcd

        self._pins = [
            digitalio.DigitalInOut(getattr(board, lcd_pins.rs)),
            digitalio.DigitalInOut(getattr(board, lcd_pins.en)),
            digitalio.DigitalInOut(getattr(board, lcd_pins.d4)),
            digitalio.DigitalInOut(getattr(board, lcd_pins.d5)),
            digitalio.DigitalInOut(getattr(board, lcd_pins.d6)),
            digitalio.DigitalInOut(getattr(board, lcd_pins.d7)),
        ]

        self.lcd = characterlcd.Character_LCD_Mono(*self._pins, columns, rows)
        self.lcd.clear()

    def update(self, line1: str, line2: str) -> None:
        line1 = line1[:16].ljust(16)
        line2 = line2[:16].ljust(16)
        self.lcd.clear()
        sleep(0.2)
        self.lcd.message = f"{line1}\n{line2}"

    def cleanup(self) -> None:
        self.lcd.clear()
        for pin in self._pins:
            pin.deinit()


def create_sensor():
    import board
    import adafruit_ahtx0

    return adafruit_ahtx0.AHTx0(board.I2C())


def read_temp_f(sensor) -> float:
    return c_to_f(sensor.temperature)


def create_serial_connection(config: RuntimeConfig):
    import serial

    try:
        serial_connection = serial.Serial(
            port=config.uart_port,
            baudrate=config.uart_baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=config.uart_timeout_seconds,
        )
        print(f"UART ready on {config.uart_port}")
        return serial_connection
    except Exception as exc:
        print("UART unavailable, continuing without serial:", exc)
        return None


def create_leds(config: RuntimeConfig):
    from gpiozero import PWMLED

    return PWMLED(config.pins.red_led), PWMLED(config.pins.blue_led)


def create_buttons(config: RuntimeConfig):
    from gpiozero import Button

    return (
        Button(
            config.pins.mode_button,
            pull_up=False,
            bounce_time=config.button_bounce_seconds,
        ),
        Button(
            config.pins.up_button,
            pull_up=False,
            bounce_time=config.button_bounce_seconds,
        ),
        Button(
            config.pins.down_button,
            pull_up=False,
            bounce_time=config.button_bounce_seconds,
        ),
    )


def button_pressed(button) -> bool:
    # External pull-up circuit: unpressed = 1, pressed = 0.
    return button.value == 0


def apply_led_action(action: LedAction, red_led, blue_led) -> None:
    red_led.off()
    blue_led.off()

    if action == "off":
        return
    if action == "heat_fade":
        red_led.pulse(fade_in_time=1, fade_out_time=1, background=True)
        return
    if action == "heat_solid":
        red_led.on()
        return
    if action == "cool_fade":
        blue_led.pulse(fade_in_time=1, fade_out_time=1, background=True)
        return
    if action == "cool_solid":
        blue_led.on()
        return

    raise ValueError(f"Unknown LED action: {action}")
