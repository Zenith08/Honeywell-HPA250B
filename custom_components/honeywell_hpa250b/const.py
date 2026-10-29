DOMAIN = "honeywell_hpa250b"
PLATFORMS = ["fan", "button"]

CONF_ADDRESS = "address"

SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"
WRITE_UUID = "0000ffe9-0000-1000-8000-00805f9b34fb"
STATUS_UUID = "0000ffe4-0000-1000-8000-00805f9b34fb"

# Commands are 20 bytes. The final bytes are padding, as observed in testing.
COMMANDS = {
    "off_toggle": bytes.fromhex("a5 01 00 93 16 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"),
    "germ":       bytes.fromhex("a5 02 00 93 16 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"),
    "general":    bytes.fromhex("a5 04 00 93 16 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"),
    "allergen":   bytes.fromhex("a5 08 00 93 16 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"),
    "turbo":      bytes.fromhex("a5 10 00 93 16 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"),
    "light_cycle":bytes.fromhex("a5 00 04 93 16 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"),
    "timer_up":   bytes.fromhex("a5 00 01 93 16 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"),
    "timer_down": bytes.fromhex("a5 00 02 93 16 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"),
    "voc_toggle": bytes.fromhex("a5 20 00 93 16 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"),
}

# Status byte values reported by the purifier, distinct from command values.
STATUS_TO_MODE = {
    0x09: "Germ",
    0x11: "General",
    0x21: "Allergen",
    0x41: "Turbo",
}
MODE_TO_COMMAND = {
    "Germ": "germ",
    "General": "general",
    "Allergen": "allergen",
    "Turbo": "turbo",
}
