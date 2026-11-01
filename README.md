# Panasonic ALaúno (アラウーノ) for Home Assistant

[日本語版 / Japanese](README.ja.md)

An **unofficial** Home Assistant custom integration for Panasonic ALaúno toilets (tested with the S160 Type 1K, model `CH1601WSSK`). It reads the same cloud data the Alauno smartphone app shows.

> **Disclaimer**: This project is not affiliated with, endorsed by, or supported by Panasonic. It uses the app's private cloud API, which can change or stop working at any time. Use it at your own risk, only with your own account and your own devices, and check the terms of service that apply to you.
>
> **No support**: This is a personal hobby project provided as-is, with no support. Issues and pull requests may not receive a response.

## Features

For each toilet you select, the integration creates a device with the following entities (usually 6 per toilet; the care sensors depend on the items the cloud reports for your model):

| Entity | Type | Meaning |
|---|---|---|
| Last used | sensor (timestamp) | Time of the most recent use |
| Today's uses | sensor | Number of uses today |
| Detergent tank | binary sensor (problem) | Detergent needs refilling |
| Deodorizing filter | binary sensor (problem) | Deodorizing filter needs replacing |
| Cleaning nozzle | binary sensor (problem) | Nozzle needs cleaning or replacing |
| Remote battery | binary sensor (problem) | Remote control battery is low |

Entity names follow your Home Assistant language (English or Japanese).

The care binary sensors expose attributes such as `level`, `first_notified_date`, `last_cared_date` and `howto_url`.

Data is polled from the cloud every 5 minutes (not real time).

## Not supported

The toilets have no local API (no open TCP ports, no ECHONET Lite response), so this integration depends on Panasonic's cloud. Monthly electricity/water reports are **not available**: the Alauno app does not offer them for this model, and although the cloud side shows traces of such a feature, it is not actually usable.

## Installation

### HACS (custom repository)

1. HACS -> three dots (top right) -> **Custom repositories**.
2. Add this repository's URL with category **Integration**.
3. Install **Panasonic ALaúno** and restart Home Assistant.

### Manual

Copy `custom_components/alauno` into your Home Assistant `config/custom_components/` folder and restart.

## Setup

1. **Settings -> Devices & services -> Add integration -> Panasonic ALaúno**.
2. **Right-click the login link in the dialog and copy it** (do not just click it). Open a **new private/incognito window**, open the browser developer tools (Network tab) first, then paste the link and log in with your CLUB Panasonic ID.
3. After login the browser tries to open a URL starting with `com.panasonic.jp.kbsbu.alauno://...`. The browser cannot open it, but the request `callback?code=...` appears (in red) in the Network tab. Copy its full URL (or just the `code` value) into the dialog. The code expires after about a minute, so paste it promptly.
4. Enter the `x-api-key` that the app sends with its requests. This value is app-specific and is **not** included in this repository; you must obtain it yourself.
5. Choose which toilets to import.

> **Note**: Do not log out of the Alauno smartphone app after setting this up. Logging out revokes the token the integration uses, and you will have to remove and re-add the integration.

## Known limitations

- No re-authentication flow yet. If the token is revoked, remove and re-add the integration.
- Polling every 5 minutes.
- The unofficial API may change without notice.
- Tested only on the model above and Home Assistant 2026.10.

## License

MIT. See [LICENSE](LICENSE). How it was built: [docs/how-it-was-built.md](docs/how-it-was-built.md).
