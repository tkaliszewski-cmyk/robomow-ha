# Robomow for Home Assistant

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

Unofficial Home Assistant integration for Robomow robot mowers.

> **Disclaimer:** This is an unofficial, community-made integration not affiliated with Robomow or MTD Products.
> It uses an undocumented API and may break if Robomow changes their cloud service.
> Use at your own risk.

---

## How it works

The Robomow app communicates with your mower through Robomow's cloud servers — not directly over your local network. This integration does the same thing: it logs into the Robomow cloud with your account credentials and asks for your mower's current status every 5 minutes.

**Your mower must be connected to your WiFi** for the cloud to have up-to-date information. If the mower loses WiFi (weak signal at the dock, low battery, etc.) the cloud will keep returning the last known values — the integration will show stale data until the mower reconnects. There is no way to detect this from the outside; it is a limitation of how the Robomow cloud works.

---

## Requirements

- A Robomow account (the same email and password you use in the Robomow app)
- Your mower's serial number (printed on a label on the mower, e.g. `AB12CD34567`)
- The mower connected to your WiFi network

---

## Installation

### Via HACS (recommended)

1. Open HACS → **Integrations** → ⋮ → **Custom repositories**
2. Add `https://github.com/tkaliszewski-cmyk/robomow-ha`, category **Integration**
3. Find **Robomow** in HACS and click **Download**
4. Restart Home Assistant

### Manual

Copy the `custom_components/robomow/` folder into your HA `config/custom_components/` directory and restart.

---

## Setup

1. **Settings → Devices & Services → Add Integration → search Robomow**
2. Enter your Robomow account **email** and **password**
3. Enter your mower's **serial number**

The integration tests your credentials and serial number before saving. If something is wrong it will tell you which field failed.

---

## Entities

| Entity | Description |
|---|---|
| **Robomow Battery** | Battery level (%) |
| **Robomow Activity** | What the mower is currently doing — see table below |
| **Robomow Stop Reason** | Why the mower last stopped — useful for automations and alerts |
| **Robomow Robot State** | Raw state code from the API (diagnostic, hidden by default) |

### Stop Reason values

| Value | Meaning |
|---|---|
| None | No stop event recorded |
| Mowing complete | Session ended normally |
| Fault / stuck | Mower needs help — check it |
| Low battery | Self-returned to charge |
| Manual stop | Stopped via button or app |
| No wire signal | Base station or perimeter wire issue |
| Unknown (n) | An unrecognised code — please open an issue |

The **Stop Reason** sensor is most useful in a HA automation: notify when it changes to `Fault / stuck` so you know the mower needs attention.

### Activity values

| Value | Meaning |
|---|---|
| Docked | At the base station |
| Mowing | Out mowing |
| Returning to base | On its way back |
| Idle | Powered on but not doing anything |
| Off | Powered off |
| Unknown (n) | An unrecognised state code — please open an issue |

---

## Supported models

Developed and tested with **Robomow RKS1500**. Other Robomow models that use the same mobile app should work — please open an issue if yours does not.

---

## Limitations

- **Read-only** — this integration only reports status. It does not send mowing commands.
- **Cloud-dependent** — requires internet access and Robomow's servers to be available.
- **5-minute poll** — status updates are not instant; there is up to a 5-minute delay.
- **Stale data when offline** — if the mower is not on WiFi, the values shown are the last known values from before it went offline.
