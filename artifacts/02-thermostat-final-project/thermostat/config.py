from dataclasses import dataclass, field

DEFAULT_SET_POINT = 72


@dataclass(frozen=True)
class PinConfig:
    """GPIO pins verified by circuit tests."""

    red_led: int = 18
    blue_led: int = 23
    mode_button: int = 24
    up_button: int = 25
    down_button: int = 12


@dataclass(frozen=True)
class LcdPinConfig:
    """Board pin names used by the character LCD."""

    rs: str = "D17"
    en: str = "D27"
    d4: str = "D5"
    d5: str = "D6"
    d6: str = "D13"
    d7: str = "D26"


@dataclass(frozen=True)
class RuntimeConfig:
    default_set_point: int = DEFAULT_SET_POINT
    uart_port: str = "/dev/ttyS0"
    uart_baudrate: int = 115200
    uart_timeout_seconds: int = 1
    lcd_columns: int = 16
    lcd_rows: int = 2
    lcd_update_seconds: int = 10
    loop_sleep_seconds: float = 0.2
    uart_update_seconds: int = 30
    button_bounce_seconds: float = 0.1
    pins: PinConfig = field(default_factory=PinConfig)
    lcd_pins: LcdPinConfig = field(default_factory=LcdPinConfig)
