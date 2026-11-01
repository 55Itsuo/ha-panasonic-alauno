# How it was built / 作り方の記録

This note explains the approach so others can judge it and reproduce the *method* for their own devices. It deliberately leaves out secrets (the app's `x-api-key`, tokens, serial numbers, addresses).

この文書は、手法を知って自分の機器でも再現できるようにするための記録です。秘密情報（アプリの `x-api-key`、トークン、シリアル番号、住所など）は載せていません。

## 1. Is there a local API? / ローカルAPIはあるか

No. From the LAN, the toilets were probed:

- All TCP ports 1-1024 (plus some extras) were closed.
- ECHONET Lite (UDP 3610) did not answer.

So the toilets are cloud-only, and the only realistic data source is what the smartphone app already receives.

ローカルからの確認では、TCP 1-1024 などは閉じており、ECHONET Lite（UDP 3610）にも応答がありませんでした。クラウド経由しか手段がないと判断しました。

## 2. Observing the app's own traffic / アプリ自身の通信を観察

Using a proxy (mitmproxy in WireGuard mode) on the author's own network, the author's own phone and own account were observed while using the app. The app talks REST/JSON to a single API host. The following was learned:

- Authentication is OAuth 2.0 / OpenID Connect (Auth0) with the PKCE authorization-code flow and `offline_access`, so a refresh token is issued. The access token lives about 24 hours.
- Requests carry `Authorization: Bearer <token>`, a static app-embedded `x-api-key`, an `x-timestamp` header (`YYYYMMDDHHMMSS+0900`) and a mobile browser User-Agent.
- The redirect URI uses the app's custom URL scheme, so a normal browser cannot complete the redirect. That is why the setup asks the user to copy the `callback?code=...` request from the browser developer tools.

アプリ通信は REST/JSON で、認証は Auth0 の PKCE（認可コード）＋ `offline_access` です。リダイレクト先がアプリ独自スキームのため、ブラウザでは完了せず、開発者ツールからコールバックURLをコピーする方式にしています。

## 3. Endpoints used / 使っているエンドポイント

All under the app's `/v2/alauno/` API:

| Path | Purpose |
|---|---|
| `/devices/info` | list of toilets |
| `/care/info?appliance_id=` | care items: detergent, deodorant filter, nozzle, remote battery |
| `/mimamori/records?date=` | usage records for a day (timestamps like `20261030192348+0900`) |
| `/user/overview` | account overview |

A monthly energy/water report exists in the data model (`energy_info.latest_report` in the overview), but no endpoint that returns it was found and the app has no screen for it, so it is not supported.

## 4. The integration / 統合の構成

- `api.py`: PKCE helpers, token exchange and refresh (rotated refresh tokens are saved), and a small client with one retry on HTTP 401.
- `coordinator.py`: a `DataUpdateCoordinator` that polls every 5 minutes and builds per-toilet data.
- `config_flow.py`: login URL -> paste callback URL / code and `x-api-key` -> choose devices.
- `sensor.py`, `binary_sensor.py`, `entity.py`: the entities.

## 5. Caveats / 注意

- Everything here depends on a private API that may change.
- Logging out of the app revokes the refresh token.
- Only use this with your own account and devices, and respect the terms that apply to you.
- Please do not publish keys, tokens, serial numbers, or captured traffic in issues.
