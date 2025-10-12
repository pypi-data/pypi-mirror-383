# DIYA_Voice/__init__.py
# Package initialization for DIYA_Voice
# Imports all main functions for voice recognition, GUI, and ESP32 control

from .core import (
    connect_serial,
    send_to_esp32,
    LED_GUI,
    load_model,
    start_mic,
    listen_once,
    parse_command,
    current_rgb,
    check_exit,
    cleanup
)
from .utils import ensure_model, auto_input_device

__all__ = [
    "connect_serial",
    "send_to_esp32",
    "LED_GUI",
    "load_model",
    "start_mic",
    "listen_once",
    "parse_command",
    "current_rgb",
    "check_exit",
    "cleanup",
    "ensure_model",
    "auto_input_device"
]
