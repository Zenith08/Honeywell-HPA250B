# Honeywell HPA250B Integration

This is an integration for Home Assistant for Honeywell Air Purifiers. They were originally sold as Bluetooth compatible but the official app for this has been long since discontinued. It provides basic fan control and mode control, but the protocol uses button presses as signals rather than setting values for some options.

## Supported Actions

- Turn the purifier on into Germ, General, Allergen, or Turbo mode.
  - You cannot turn it "on" you must select 1 mode. This is a known issue.
- Toggle VOC Sensor Mode.
- Increment or Decrement the timer time remaining.
- Toggle the LED brightness.

## Setup

To set up the integration you must have the Mac address of the bluetooth device to connect to. This can be retrieved with a bluetooth scanner.

## Credits and References

- ChatGPT was used for most of development especially reverse-engineering the protocol.
- This repository is based off the [Template by Joakim Sørensen](https://github.com/ludeeus/integration_blueprint/tree/main)
