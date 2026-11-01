"""Config flow: PKCE login via pasted callback URL."""
from __future__ import annotations

import secrets
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from . import api
from .const import CONF_API_KEY, CONF_DEVICES, CONF_REFRESH_TOKEN, DOMAIN


class AlaunoConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._verifier, challenge = api.new_pkce()
        self._state = secrets.token_urlsafe(24)
        self._auth_url = api.build_authorize_url(challenge, self._state)
        self._api_key = ""
        self._refresh_token = ""
        self._devices: list[dict] = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            session = async_get_clientsession(self.hass)
            try:
                code = api.extract_code(user_input["callback"])
                tokens = await api.exchange_code(session, code, self._verifier)
                self._api_key = user_input[CONF_API_KEY].strip()
                self._refresh_token = tokens["refresh_token"]
                client = api.AlaunoClient(session, self._api_key, self._refresh_token)
                self._devices = await client.devices()
                if client._refresh_token != self._refresh_token:
                    self._refresh_token = client._refresh_token
            except api.AlaunoAuthError:
                errors["base"] = "auth"
            except Exception:  # noqa: BLE001
                errors["base"] = "cannot_connect"
            else:
                return await self.async_step_devices()
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("callback"): str,
                    vol.Required(CONF_API_KEY): str,
                }
            ),
            description_placeholders={"auth_url": self._auth_url},
            errors=errors,
        )

    async def async_step_devices(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        options = {
            d["appliance_id"]: d["appliance_info"].get("nickname") or d["appliance_id"][:8]
            for d in self._devices
        }
        if user_input is not None:
            await self.async_set_unique_id(DOMAIN)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title="Panasonic アラウーノ",
                data={
                    CONF_API_KEY: self._api_key,
                    CONF_REFRESH_TOKEN: self._refresh_token,
                    CONF_DEVICES: user_input[CONF_DEVICES],
                },
            )
        return self.async_show_form(
            step_id="devices",
            data_schema=vol.Schema(
                {vol.Required(CONF_DEVICES, default=[]): cv.multi_select(options)}
            ),
        )
