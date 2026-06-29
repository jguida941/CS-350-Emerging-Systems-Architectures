from .controller import Mode


def format_uart_message(mode: Mode, temp_f: float, set_point: int) -> str:
    return f"{mode},{temp_f:.1f},{set_point}\n"


def send_uart(serial_connection, mode: Mode, temp_f: float, set_point: int) -> None:
    message = format_uart_message(mode, temp_f, set_point)
    print("UART:", message.strip())

    if serial_connection is not None:
        serial_connection.write(message.encode("utf-8"))
