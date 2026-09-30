"""EasyView API client for Medtrum CGM sensors."""

from __future__ import annotations

import asyncio
import logging
import socket
from typing import Any

import aiohttp

from .const import API_TIME_OUT_SECONDS, BASE_URL, LOGIN_ENDPOINT, STATUS_ENDPOINT

_LOGGER = logging.getLogger(__name__)


class EasyViewApiClient:
    """Handles authenticated communication with the EasyView cloud API."""

    def __init__(self, username: str, password: str, session: aiohttp.ClientSession) -> None:
        self._username = username
        self._password = password
        self._session = session
        self._logged_in = False

    async def async_login(self) -> None:
        """Authenticate with EasyView and store session cookie."""
        data = {
            "apptype": "Follow",
            "user_name": self._username,
            "password": self._password,
            "platform": "google",
            "user_type": "M",
        }
        response = await _api_wrapper(
            self._session,
            method="post",
            url=f"{BASE_URL}/{LOGIN_ENDPOINT}",
            data=data,
        )
        if response.get("res") == "ERR":
            raise EasyViewApiAuthenticationError(
                f"Login failed: {response.get('msg', 'unknown error')}"
            )
        self._logged_in = True
        _LOGGER.debug("Logged in to EasyView as %s", self._username)

    async def async_get_data(self) -> dict[str, Any]:
        """Fetch current sensor status from EasyView."""
        if not self._logged_in:
            await self.async_login()

        response = await _api_wrapper(
            self._session,
            method="get",
            url=f"{BASE_URL}/{STATUS_ENDPOINT}",
        )

        if response.get("res") == "ERR":
            if "login" in str(response.get("msg", "")).lower():
                _LOGGER.warning("Session expired, re-authenticating")
                self._logged_in = False
                await self.async_login()
                response = await _api_wrapper(
                    self._session,
                    method="get",
                    url=f"{BASE_URL}/{STATUS_ENDPOINT}",
                )
            else:
                raise EasyViewApiError(f"API error: {response.get('msg', 'unknown')}")

        monitor_list = response.get("monitorlist", [])
        if not monitor_list:
            raise EasyViewApiError("No monitored users found in EasyView account")

        results = []
        for entry in monitor_list:
            sensor_status = entry.get("sensor_status")
            if sensor_status is None:
                _LOGGER.warning("No active sensor for user %s", entry.get("username"))
                continue
            results.append(
                {
                    "username": entry.get("username", "Unknown"),
                    "patient_name": (
                        entry.get("alias")
                        or entry.get("real_name")
                        or entry.get("data", {}).get("follow_alias")
                        or entry.get("username", "Unknown")
                    ),
                    "sensor_status": sensor_status,
                }
            )

        if not results:
            raise EasyViewApiError("No active sensors found")

        return results


async def _api_wrapper(
    session: aiohttp.ClientSession,
    method: str,
    url: str,
    data: dict | None = None,
    headers: dict | None = None,
) -> dict[str, Any]:
    """Perform an HTTP request with timeout and error handling."""
    try:
        async with asyncio.timeout(API_TIME_OUT_SECONDS):
            if method == "post":
                response = await session.post(url, data=data, headers=headers)
            else:
                response = await session.get(url, params=data, headers=headers)
    except asyncio.TimeoutError as exc:
        raise EasyViewApiCommunicationError("Timeout error fetching information") from exc
    except (aiohttp.ClientError, socket.gaierror) as exc:
        raise EasyViewApiCommunicationError("Error fetching information") from exc
    except Exception as exc:
        raise EasyViewApiError("Unexpected error") from exc

    _LOGGER.debug("HTTP %s %s → %s", method.upper(), url, response.status)

    if response.status in (401, 403):
        raise EasyViewApiAuthenticationError("Invalid credentials")

    try:
        response.raise_for_status()
        return await response.json(content_type=None)
    except (aiohttp.ClientError, socket.gaierror) as exc:
        raise EasyViewApiCommunicationError("Error reading response") from exc
    except Exception as exc:
        raise EasyViewApiError("Unexpected error parsing response") from exc


class EasyViewApiError(Exception):
    """General EasyView API error."""


class EasyViewApiCommunicationError(EasyViewApiError):
    """Communication error with EasyView API."""


class EasyViewApiAuthenticationError(EasyViewApiError):
    """Authentication error with EasyView API."""