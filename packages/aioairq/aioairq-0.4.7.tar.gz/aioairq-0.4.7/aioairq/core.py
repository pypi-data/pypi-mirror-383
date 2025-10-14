from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, List, Literal, TypedDict

import aiohttp

from aioairq.encrypt import AESCipher
from aioairq.exceptions import (
    APIAccessDenied,
    APIAccessError,
    InvalidAirQResponse,
    InvalidIpAddress,
)
from aioairq.utils import is_time_in_interval, is_valid_ipv4_address

_LOGGER = logging.getLogger(__name__)

LedThemeName = Literal[
    "standard",
    "standard (contrast)",
    "Virus",
    "Virus (contrast)",
    "co2_covid19",
    "CO2",
    "VOC",
    "Humidity",
    "CO",
    "NO2",
    "O3",
    "Oxygen",
    "PM1",
    "PM2.5",
    "PM10",
    "Noise",
    "Noise (contrast)",
    "Noise Average",
    "Noise Average (contrast)",
]


class DeviceInfo(TypedDict):
    """Container for device information"""

    id: str
    name: str | None
    model: str | None
    suggested_area: str | None
    sw_version: str | None
    hw_version: str | None


class DeviceLedTheme(TypedDict, total=True):
    """Complete specification of the LED themes of a device.

    Each device is described by two themes, one for each side.
    """

    left: LedThemeName
    right: LedThemeName


class DeviceLedThemePatch(TypedDict, total=False):
    """Potentially incomplete specification of the LED themes.

    Helpful for updating the themes.
    """

    left: LedThemeName
    right: LedThemeName


class Brightness(TypedDict):
    """LED brightness in %"""

    default: float
    night: float | None


class NightMode(TypedDict):
    """Container holding night mode configuration"""

    activated: bool
    """Whether the night mode is activated"""

    start_day: str
    """End time of night mode in format 'HH:mm'. Note that the time is in UTC."""

    start_night: str
    """Start time of night mode in format 'HH:mm'. Note that the time is in UTC."""

    brightness_day: float
    """LED brightness (in percent) outside of night mode."""

    brightness_night: float
    """LED brightness (in percent) during night mode."""

    fan_night_off: bool
    """Whether the fans are turned off during night mode.
    
    Notes from official docs:
    Turning off the fans will disable the sensors for particle pollution (PM1, PM2.5, PM10).
    Fire alarm will only trigger for CO and temperature, but not for smoke."""

    wifi_night_off: bool
    """Whether Wi-Fi is turned off during night mode.
    
    Notes from official docs:
    When turning off Wi-Fi with this setting and when cloud upload is enabled,
    data will be cached on the SD card and uploaded eventually
    when network link is available again."""

    alarm_night_off: bool
    """Whether alarms are turned off during night mode.
    
    Notes from official docs:
    This setting disables acoustic warnings. Fire and gas alarm will trigger despite."""


class AirQ:
    _supported_routes = ["config", "log", "data", "average", "ping"]

    def __init__(
        self,
        address: str,
        passw: str,
        session: aiohttp.ClientSession,
        timeout: float = 15,
    ):
        """Class representing the API for a single AirQ device

        The class holds the AESCipher object, responsible for message decoding,
        as well as the anchor of the http address to base further requests on

        Parameters
        ----------
        address : str
            Either the IP address of the device, or its mDNS.
            Device's IP might be a more robust option (across the variety of routers)
        passw : str
            Device's password
        session : aiohttp.ClientSession
            Session used to communicate to the device. Should be managed by the user
        timeout : float
            Maximum time in seconds used by `session.get` to connect to the device
            before `aiohttp.ServerTimeoutError` is raised. Default: 15 seconds.
            Hitting the timeout be an indication that the device and the host are not
            on the same WiFi
        """

        self.address = address
        self.anchor = "http://" + self.address
        self.aes = AESCipher(passw)
        self._session = session
        self._timeout = aiohttp.ClientTimeout(total=timeout)
        self._previous_data: dict = {}

    async def has_api_access(self) -> bool:
        return (await self.get_config())["APIaccess"]

    async def blink(self) -> str:
        """Let the device blink in rainbow colors for a short amount of time.

        Returns the device's ID.
        This function can be used to identify a device, when you have multiple devices.
        """
        json_data = await self._get_json("/blink")
        _LOGGER.debug("Received the blink command")

        return json_data["id"]

    async def validate(self) -> None:
        """Test if the password provided to the constructor is valid.

        Raises InvalidAuth if the password is not correct.
        This is merely a convenience function, relying on the exception being
        raised down the stack (namely by AESCipher.decode from within self.get)
        """
        _LOGGER.debug("Checking the access to the device")
        await self.get("ping")

    async def restart(self) -> None:
        """Restarts the device."""
        post_json_data = {"reset": True}
        _LOGGER.info("Received the restart command")

        await self._post_json_and_decode("/config", post_json_data)

    async def shutdown(self) -> None:
        """Shuts the device down."""
        post_json_data = {"shutdown": True}
        _LOGGER.info("Received the shutdown command")

        await self._post_json_and_decode("/config", post_json_data)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.address})"

    async def fetch_device_info(self) -> DeviceInfo:
        """Fetch condensed device description"""
        _LOGGER.debug("Fetching device info")
        config: dict = await self.get("config")
        room_type = config.get("RoomType")

        try:
            # The only required field. Should not really be missing, just a precaution
            device_id = config["id"]
        except KeyError as e:
            raise InvalidAirQResponse from e

        device_info = DeviceInfo(
            id=device_id,
            name=config.get("devicename"),
            model=config.get("type"),
            suggested_area=room_type.replace("-", " ").title() if room_type else None,
            sw_version=config.get("air-Q-Software-Version"),
            hw_version=config.get("air-Q-Hardware-Version"),
        )
        _LOGGER.debug("Fetched device_info %s", device_info)
        return device_info

    @staticmethod
    def drop_uncertainties_from_data(data: dict) -> dict:
        """Filter returned dict and substitute [value, uncertainty] with the value.

        The device attempts to estimate the uncertainty, or error, of certain readings.
        These readings are returned as tuples of (value, uncertainty). Often, the latter
        is not desired, and this is a convenience method to homogenise the dict a little
        """
        # `if v else None` is a precaution for the case of v being an empty list
        # (which ought not to happen really...)
        return {
            k: (v[0] if v else None) if isinstance(v, (list, tuple)) else v
            for k, v in data.items()
        }

    @staticmethod
    def clip_negative_values(data: dict) -> dict:
        _msg_template = "clipping value for %s: %.2f -> 0.0"

        def clip(key: str, value):
            if isinstance(value, list):
                if value[0] < 0:
                    _LOGGER.debug(_msg_template, key, value[0])
                return [max(0, value[0]), value[1]]
            if isinstance(value, (float, int)):
                if value < 0:
                    _LOGGER.debug(_msg_template, key, value)
                return max(0, value)

            return value

        return {k: clip(k, v) for k, v in data.items()}

    async def get_latest_data(
        self,
        return_average=True,
        clip_negative_values=True,
        return_uncertainties=False,
        return_original_keys=False,
    ) -> dict:
        """Poll the dictionary with the momentary values from the device.

        Parameters
        ----------
        return_average : bool, default is True
            The device exposes both the raw momentary data as well as their
            rolling / exponential averages. To access the former, set this to False.
        clip_negative_values : bool, default is True
            For brief periods, mostly during self-calibration, the device may return
            negative sensor values. A conventional solution is to clip them to 0.
        return_uncertainties : bool, default is False
            For certain sensors, the device exposes not only the momentary value
            but also an estimate of its uncertainty. If this parameter is set to True,
            the values of those sensors will be returned as lists of length 2: [value, uncertainty].
        return_original_keys : bool, default is False
            Currently, depending on configuration, the device expose the particulate
            matter values under two different set of keys: `pm{1,2_5,10}` and `pm{1,2_5,10}_SPS30`.
            By default, this method strips the `_SPS30` suffix to offer a more homogineous
            structure of the returned dict.
        """

        route = "average" if return_average else "data"
        _LOGGER.debug("Fetching from %s", route)
        data = await self.get(route)
        if clip_negative_values:
            _LOGGER.debug("Clippig negative values")
            data = self.clip_negative_values(data)
        if not return_uncertainties:
            _LOGGER.debug("Dropping uncertainties")
            data = self.drop_uncertainties_from_data(data)
        if not return_original_keys:
            data = {self._homogenise_key(key): value for key, value in data.items()}
        if _LOGGER.isEnabledFor(logging.DEBUG):
            self._compare_to_previous(data)
        return data

    def _compare_to_previous(self, data: dict) -> None:
        if self._previous_data:
            ComparisonSummary.compare(data, self._previous_data).report()
        else:
            _LOGGER.debug("No previous data cached, initialting with the current")
        self._previous_data = data

    def _homogenise_key(self, key: str) -> str:
        """Meant to capture various changes to the original keys.

        Currently it only strips `_SPS30` suffix from the keys of the particulate
        values from a new sensor, allowing all PM values to appear under the same keys
        disregarding the underlying sensor configuration.
        """
        _SUFFIX = "_SPS30"
        if _SUFFIX in key:
            _LOGGER.debug("Dropping %s from %s", _SUFFIX, key)
        return key.replace(_SUFFIX, "")

    async def get(self, subject: str) -> dict:
        """Return the given subject from the air-Q device.

        This function only works on a limited set of subject specified in _supported_routes.
        Prefer using more specialized functions."""
        if subject not in self._supported_routes:
            raise NotImplementedError(
                "AirQ.get() is currently limited to a set of requests, returning "
                f"a dict with a key 'content' (namely {self._supported_routes})."
            )

        _LOGGER.debug("Fetching from %s", subject)
        return await self._get_json_and_decode("/" + subject)

    async def _get_json(self, relative_url: str) -> dict:
        """Executes a GET request to the air-Q device with the configured timeout
        and returns JSON data as a dictionary.

        relative_url is expected to start with a slash."""

        async with self._session.get(
            f"{self.anchor}{relative_url}", timeout=self._timeout
        ) as response:
            json_string = await response.text()

        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            raise InvalidAirQResponse(
                "_get_json() must only be used to query endpoints returning JSON data. "
                f"{relative_url} returned {json_string}."
            ) from e

    async def _get_json_and_decode(self, relative_url: str) -> Any:
        """Executes a GET request to the air-Q device with the configured timeout
        decodes the response and returns JSON data.

        relative_url is expected to start with a slash."""

        json_data = await self._get_json(relative_url)

        encoded_message = json_data["content"]
        decoded_json_data = self.aes.decode(encoded_message)
        _LOGGER.debug("%s returned %s", relative_url, decoded_json_data)

        return json.loads(decoded_json_data)

    async def _post_json_and_decode(
        self, relative_url: str, post_json_data: dict
    ) -> Any:
        """Executes a POST request to the air-Q device with the configured timeout,
        decodes the response and returns JSON data.

        relative_url is expected to start with a slash."""

        post_json_data_str = json.dumps(post_json_data)
        _LOGGER.debug("Posting %s to %s", post_json_data_str, relative_url)
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        post_data = "request=" + self.aes.encode(post_json_data_str)

        async with self._session.post(
            f"{self.anchor}{relative_url}",
            headers=headers,
            data=post_data,
            timeout=self._timeout,
        ) as response:
            json_string = await response.text()

        _LOGGER.debug("Received %s from %s", json_string, relative_url)
        try:
            json_data = json.loads(json_string)
        except json.JSONDecodeError as e:
            raise InvalidAirQResponse(
                "_post_json() must only be used to query endpoints returning JSON data. "
                f"{relative_url} returned {json_string}."
            ) from e

        encoded_message = json_data["content"]
        decoded_json_data = self.aes.decode(encoded_message)

        _LOGGER.debug("Decoded %s from %s", json_string, relative_url)
        response_decoded = json.loads(decoded_json_data)
        if isinstance(response_decoded, str) and response_decoded.startswith("Error"):
            _lookup_exception_from_firmware_response(response_decoded)
        return response_decoded

    @property
    async def data(self):
        return await self.get("data")

    @property
    async def average(self):
        return await self.get("average")

    @property
    async def config(self):
        """Deprecated. Use get_config() instead."""
        return await self.get("config")

    async def set_ifconfig_static(self, ip: str, subnet: str, gateway: str, dns: str):
        """Configures the interface to use a static IP setup.

        Notice: The air-Q only supports IPv4. After calling this function,
        you should call restart() to apply the settings."""
        if not is_valid_ipv4_address(ip):
            raise InvalidIpAddress(f"Invalid IP address: {ip}")
        if not is_valid_ipv4_address(subnet):
            raise InvalidIpAddress(f"Invalid subnet address: {subnet}")
        if not is_valid_ipv4_address(gateway):
            raise InvalidIpAddress(f"Invalid gateway address: {gateway}")
        if not is_valid_ipv4_address(dns):
            raise InvalidIpAddress(f"Invalid DNS server address: {dns}")

        post_json_data = {
            "ifconfig": {"ip": ip, "subnet": subnet, "gateway": gateway, "dns": dns}
        }

        await self._post_json_and_decode("/config", post_json_data)

    async def set_ifconfig_dhcp(self):
        """Configures the interface to use DHCP.

        Notice: After calling this function, you should call restart() to apply the settings.
        """
        post_json_data = {"DeleteKey": "ifconfig"}

        await self._post_json_and_decode("/config", post_json_data)

    async def get_time_server(self):
        return (await self.get_config())["TimeServer"]

    async def set_time_server(self, time_server):
        post_json_data = {"TimeServer": time_server}

        try:
            return await self._post_json_and_decode("/config", post_json_data)
        except APIAccessDenied:
            # convert the culprit key as it is used by the firmware
            # to the name of this specific class method
            raise APIAccessDenied("set_time_server is only supported for air-Q Science")

    async def get_device_name(self):
        return (await self.get_config())["devicename"]

    async def set_device_name(self, device_name):
        post_json_data = {"devicename": device_name}

        await self._post_json_and_decode("/config", post_json_data)

    async def get_cloud_remote(self) -> bool:
        return (await self._get_json_and_decode("/config"))["cloudRemote"]

    async def set_cloud_remote(self, value: bool):
        post_json_data = {"cloudRemote": value}

        await self._post_json_and_decode("/config", post_json_data)

    async def get_log(self) -> List[str]:
        return await self._get_json_and_decode("/log")

    async def get_config(self) -> dict:
        return await self._get_json_and_decode("/config")

    async def get_possible_led_themes(self) -> List[LedThemeName]:
        return (await self._get_json_and_decode("/config"))["possibleLedTheme"]

    async def get_led_theme(self) -> DeviceLedTheme:
        led_theme = (await self._get_json_and_decode("/config"))["ledTheme"]

        return DeviceLedTheme(left=led_theme["left"], right=led_theme["right"])

    async def set_led_theme(self, theme: DeviceLedThemePatch | DeviceLedTheme):
        # air-Q does not support setting only one side.
        # If you do this, the API will answer a misleading error like
        #
        # ```
        # Error: unsupported option for key 'ledTheme' - can be ['standard', 'standard (contrast)', ...]
        # ```
        #
        # Therefore, we first read both sides, so we may set both sides at once.

        # I am not too satisfied with the DeviceLedThemePatch|DeviceLedTheme annotation,
        # necessary to pacify pyright. A better solution would be to use
        # proper inheritance, I guess, to indicate that DeviceLedTheme is a
        # subclass of DeviceLedThemePatch. Does not seem to work with TypedDict and
        # total={True,False}. Consider switching to pydantic

        if len(theme) < 2:
            current_led_theme = await self.get_led_theme()
            theme = current_led_theme | theme

        await self._post_json_and_decode("/config", {"ledTheme": theme})

    async def get_night_mode(self) -> NightMode:
        night_mode = (await self.get_config())["NightMode"]

        return NightMode(
            activated=night_mode["Activated"],
            start_day=night_mode["StartDay"],
            start_night=night_mode["StartNight"],
            brightness_day=night_mode["BrightnessDay"] * 10.0,
            brightness_night=night_mode["BrightnessNight"] * 10.0,
            fan_night_off=night_mode["FanNightOff"],
            wifi_night_off=night_mode["WifiNightOff"],
            alarm_night_off=night_mode["AlarmNightOff"],
        )

    async def set_night_mode(self, night_mode: NightMode):
        post_json_data = {
            "NightMode": {
                "Activated": night_mode["activated"],
                "StartDay": night_mode["start_day"],
                "StartNight": night_mode["start_night"],
                "BrightnessDay": night_mode["brightness_day"] / 10.0,
                "BrightnessNight": night_mode["brightness_night"] / 10.0,
                "FanNightOff": night_mode["fan_night_off"],
                "WifiNightOff": night_mode["wifi_night_off"],
                "AlarmNightOff": night_mode["alarm_night_off"],
            }
        }

        await self._post_json_and_decode("/config", post_json_data)

    async def get_brightness_config(self) -> Brightness:
        night_mode = await self.get_night_mode()

        return Brightness(
            default=night_mode["brightness_day"],
            night=night_mode["brightness_night"],
        )

    async def set_brightness_config(
        self, default: float | None = None, night: float | None = None
    ) -> None:
        if not isinstance(default, (int, float, type(None))):
            raise ValueError(f"Unsupported {type(default)=}")
        if not isinstance(night, (int, float, type(None))):
            raise ValueError(f"Unsupported {type(night)=}")
        if default is not None and ((default < 0) or (default > 100)):
            raise ValueError(f"if given, default must be in [0, 100] got {default}")
        if night is not None and ((night < 0) or (night > 10)):
            raise ValueError(f"if given, night must be in [0, 10] got {night}")

        current_night_mode = await self.get_night_mode()
        if default is not None:
            current_night_mode.update({"brightness_day": default})
        if night is not None:
            current_night_mode.update({"brightness_night": night})
        await self.set_night_mode(current_night_mode)

    async def get_current_brightness(self) -> float:
        """Get current LED brightness in %.

        This function automatically checks if the night mode is activated
        and fetches the correct brightness.
        """
        night_mode = await self.get_night_mode()
        return night_mode[_select_current_brightness_key(night_mode)]

    async def set_current_brightness(self, value: float) -> None:
        """Set current LED brightness to the desired value in %.

        This function automatically checks if the night mode is activated
        and configures the correct brightness based on the time of the day.
        """
        if not isinstance(value, (int, float)):
            raise ValueError(f"Unsupported {type(value)=}")
        if value < 0 or value > 100:
            raise ValueError(f"Unsupported brightness {value=}, must be in [0, 100]")

        night_mode = await self.get_night_mode()
        target_key = _select_current_brightness_key(night_mode)

        if night_mode[target_key] == value:
            # spare a round of communication to the device if nothing needs changing
            return

        await self.set_night_mode(night_mode | {target_key: value})


def identify_warming_up_sensors(data: dict) -> set[str]:
    """Based on the data, identify sensors that are still warming up.

    Convenience function that extracts a list of sensor names from the
    "Status" field.
    """
    sensor_names = set()
    device_status: dict[str, str] | Literal["OK"] = data["Status"]
    if isinstance(device_status, dict):
        for sensor_name, sensor_status in device_status.items():
            if "sensor still in warm up phase" in sensor_status:
                sensor_names.add(sensor_name)
    return sensor_names


@dataclass
class ComparisonSummary:
    """Class capturing the difference between two datasets fetched from AirQ.

    Parameters
    ----------
    missing_keys : set[str]
        Dictionary keys (sensor names) present in the previous data dictionary
        but absent in the current.
    warming_up : set[str]
        Sensor names currently reported to undergo their warm up phases.
        In normal operation, should be the same as `missing_keys`.
    unaccountably_missing_keys : set[str]
        Missing keys that do not correspond to sensors reported as warming up.
        In normal operation, should be an empty set.
    new_values : dict
        Values from sensors that did not report in the previous data dictionary.
    difference : dict
        Differences between current and previous readings for sensors present
        in both dictionaries. Indexed by sensor names.

    Notes
    -----
    This class provides a structured way to track changes between two sequential
    readings from AirQ sensors, helping identify missing, warming up, and changed
    sensor values.
    """

    missing_keys: set[str] = field(default_factory=set)
    warming_up: set[str] = field(default_factory=set)
    unaccountably_missing_keys: set[str] = field(default_factory=set)
    new_values: dict = field(default_factory=dict)
    difference: dict = field(default_factory=dict)

    @classmethod
    def compare(cls, current: dict, previous: dict) -> "ComparisonSummary":
        """Given two data dictionaries reported by AirQ, generate the comparison."""

        missing_keys = set(previous).difference(current)
        warming_up = identify_warming_up_sensors(current)
        unaccountably_missing_keys = missing_keys.difference(warming_up)

        new_values = {}
        difference = {}
        for k, curr in current.items():
            if (prev := previous.get(k)) is None:
                new_values[k] = curr
            elif isinstance(curr, (int, float)) and isinstance(prev, (int, float)):
                difference[k] = curr - prev
            elif isinstance(curr, list) and isinstance(prev, list):
                difference[k] = [c - p for c, p in zip(curr, prev)]

        return cls(
            missing_keys=missing_keys,
            warming_up=warming_up,
            unaccountably_missing_keys=unaccountably_missing_keys,
            new_values=new_values,
            difference=difference,
        )

    def report(self):
        """Log the comparison at DEBUG level.

        Each field, if not empty, is reported in its own single record.
        """
        if self.missing_keys:
            _LOGGER.debug("Compared to the prev data %s are missing", self.missing_keys)
        if self.warming_up:
            _LOGGER.debug("%s are still warming up", self.warming_up)
        if self.unaccountably_missing_keys:
            _LOGGER.debug(
                "%s disappeared since the previous data and not warming up",
                self.unaccountably_missing_keys,
            )
        if self.new_values:
            _LOGGER.debug(
                "Since the previous fetch, following sensors started broadcasting: %s",
                self.new_values,
            )
        _LOGGER.debug("Difference since the previous fetch: %s", self.difference)


def _lookup_exception_from_firmware_response(error_message: str):
    """Ad hoc function attempting to parse the error message.

    Tries to recognise the error message and issue a specific error.
    If fails, issues an unspecific APIAccessError.
    """
    if m := re.match(
        r"Error: (?P<message>'.*' is only available for air-Q Science)!\n",
        error_message,
    ):
        raise APIAccessDenied(m.groupdict()["message"])
    else:
        raise APIAccessError(error_message)


def _select_current_brightness_key(
    night_mode: NightMode,
) -> Literal["brightness_day", "brightness_night"]:
    if night_mode["activated"] and is_time_in_interval(
        start=night_mode["start_night"], end=night_mode["start_day"]
    ):
        target_key = "brightness_night"
    else:
        target_key = "brightness_day"
    return target_key
