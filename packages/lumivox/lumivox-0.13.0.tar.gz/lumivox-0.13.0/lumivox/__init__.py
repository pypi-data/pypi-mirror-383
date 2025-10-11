# Lumivox package initialization
# Handles imports for voice recognition, GUI, and hardware integration

from .core import (
    connect_serial,
    send_to_esp32,
    LED_GUI,
    load_model,
    start_mic,
    listen_once,
    parse_command,
    check_exit,
    cleanup
)
from .utils import ensure_model, auto_input_device

# Make lumivox.<function> directly available
__all__ = [
    "connect_serial",
    "send_to_esp32",
    "LED_GUI",
    "load_model",
    "start_mic",
    "listen_once",
    "parse_command",
    "check_exit",
    "cleanup",
    "ensure_model",
    "auto_input_device"
]
