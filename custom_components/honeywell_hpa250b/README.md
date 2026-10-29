# Honeywell HPA250B — Home Assistant custom integration

This is an initial, locally controlled Bluetooth integration based on commands and notifications tested against a Honeywell HPA250B.

## Install

1. Copy `custom_components/honeywell_hpa250b` into your Home Assistant configuration directory's `custom_components` folder.
2. Restart Home Assistant.
3. Open **Settings → Devices & services → Add integration**.
4. Search for **Honeywell HPA250B** and enter the purifier's Bluetooth address.
5. Keep the purifier in Bluetooth range of the Home Assistant Bluetooth adapter or a configured Bluetooth proxy.

## Included entities

- Fan entity: power and General, Germ, Allergen, and Turbo presets.
- Buttons: cycle indicator light, increase timer, decrease timer, and toggle VOC mode.

The light and VOC commands are buttons because the reverse-engineered command set indicates those commands may cycle/toggle rather than explicitly set a requested state.

## Important protocol behavior

- `A5 01 ...` is a **power toggle**, not an explicit on command. From Off, it starts the purifier in General mode.
- `A5 04 ...` selects General mode but does **not** turn the purifier on from Off.
- The integration checks the latest reported power state before toggling. If state is unknown, it avoids blindly toggling power off.
- Mode command bytes and reported status bytes differ. Status values currently interpreted are `00` Off, `09` Germ, `11` General, `21` Allergen, and `41` Turbo.

## Notes / limitations

- This is a community-style custom integration, not an official Home Assistant integration.
- It has not been run against your Home Assistant installation yet. Please test and check **Settings → System → Logs** after installing.
- Bluetooth support depends on the Home Assistant host/proxy setup and the current Home Assistant / Bleak APIs.
- Status parsing for timer, filters, VOC/IAQ, and indicator light is preliminary. Those values are not exposed as sensors yet.
- Do not expose Bluetooth control to untrusted networks. Keep Home Assistant and Bluetooth devices secured.
