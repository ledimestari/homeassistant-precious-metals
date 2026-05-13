"""Sensor platform for Precious Metal Prices."""

from __future__ import annotations

import logging
import time
from datetime import timedelta
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

METAL_API_URL = "https://api.edelmetalle.de/public.json"
CURRENCY_API_URL = "https://latest.currency-api.pages.dev/v1/currencies/eur.json"

# Metal prices update every 5 minutes on the source
METAL_SCAN_INTERVAL = timedelta(minutes=5)
# Currency rates update seems even not to update once per hour?
CURRENCY_SCAN_INTERVAL = timedelta(hours=1)

# Required fields from metal API
REQUIRED_METAL_FIELDS = {
    "gold_usd",
    "gold_eur",
    "silber_usd",
    "silber_eur",
    "platin_usd",
    "platin_eur",
    "palladium_usd",
    "palladium_eur",
}

SENSORS = [
    # Gold
    {"name": "Gold USD/toz", "unit": "USD", "icon": "mdi:currency-usd"},
    {"name": "Gold USD/g", "unit": "USD", "icon": "mdi:currency-usd"},
    {"name": "Gold USD/kg", "unit": "USD", "icon": "mdi:currency-usd"},
    {"name": "Gold EUR/toz", "unit": "EUR", "icon": "mdi:currency-eur"},
    {"name": "Gold EUR/g", "unit": "EUR", "icon": "mdi:currency-eur"},
    {"name": "Gold EUR/kg", "unit": "EUR", "icon": "mdi:currency-eur"},
    {"name": "Gold GBP/toz", "unit": "GBP", "icon": "mdi:currency-gbp"},
    {"name": "Gold GBP/g", "unit": "GBP", "icon": "mdi:currency-gbp"},
    {"name": "Gold GBP/kg", "unit": "GBP", "icon": "mdi:currency-gbp"},
    {"name": "Gold CHF/toz", "unit": "CHF", "icon": "mdi:currency-fra"},
    {"name": "Gold CHF/g", "unit": "CHF", "icon": "mdi:currency-fra"},
    {"name": "Gold CHF/kg", "unit": "CHF", "icon": "mdi:currency-fra"},
    # Silver
    {"name": "Silver USD/toz", "unit": "USD", "icon": "mdi:currency-usd"},
    {"name": "Silver USD/g", "unit": "USD", "icon": "mdi:currency-usd"},
    {"name": "Silver USD/kg", "unit": "USD", "icon": "mdi:currency-usd"},
    {"name": "Silver EUR/toz", "unit": "EUR", "icon": "mdi:currency-eur"},
    {"name": "Silver EUR/g", "unit": "EUR", "icon": "mdi:currency-eur"},
    {"name": "Silver EUR/kg", "unit": "EUR", "icon": "mdi:currency-eur"},
    {"name": "Silver GBP/toz", "unit": "GBP", "icon": "mdi:currency-gbp"},
    {"name": "Silver GBP/g", "unit": "GBP", "icon": "mdi:currency-gbp"},
    {"name": "Silver GBP/kg", "unit": "GBP", "icon": "mdi:currency-gbp"},
    {"name": "Silver CHF/toz", "unit": "CHF", "icon": "mdi:currency-fra"},
    {"name": "Silver CHF/g", "unit": "CHF", "icon": "mdi:currency-fra"},
    {"name": "Silver CHF/kg", "unit": "CHF", "icon": "mdi:currency-fra"},
    {"name": "Platinum CHF/toz", "unit": "CHF", "icon": "mdi:currency-fra"},
    {"name": "Platinum CHF/g", "unit": "CHF", "icon": "mdi:currency-fra"},
    {"name": "Platinum CHF/kg", "unit": "CHF", "icon": "mdi:currency-fra"},
    # Platinum
    {"name": "Platinum USD/toz", "unit": "USD", "icon": "mdi:currency-usd"},
    {"name": "Platinum USD/g", "unit": "USD", "icon": "mdi:currency-usd"},
    {"name": "Platinum USD/kg", "unit": "USD", "icon": "mdi:currency-usd"},
    {"name": "Platinum EUR/toz", "unit": "EUR", "icon": "mdi:currency-eur"},
    {"name": "Platinum EUR/g", "unit": "EUR", "icon": "mdi:currency-eur"},
    {"name": "Platinum EUR/kg", "unit": "EUR", "icon": "mdi:currency-eur"},
    {"name": "Platinum GBP/toz", "unit": "GBP", "icon": "mdi:currency-gbp"},
    {"name": "Platinum GBP/g", "unit": "GBP", "icon": "mdi:currency-gbp"},
    {"name": "Platinum GBP/kg", "unit": "GBP", "icon": "mdi:currency-gbp"},
    # Palladium
    {"name": "Palladium USD/toz", "unit": "USD", "icon": "mdi:currency-usd"},
    {"name": "Palladium USD/g", "unit": "USD", "icon": "mdi:currency-usd"},
    {"name": "Palladium USD/kg", "unit": "USD", "icon": "mdi:currency-usd"},
    {"name": "Palladium EUR/toz", "unit": "EUR", "icon": "mdi:currency-eur"},
    {"name": "Palladium EUR/g", "unit": "EUR", "icon": "mdi:currency-eur"},
    {"name": "Palladium EUR/kg", "unit": "EUR", "icon": "mdi:currency-eur"},
    {"name": "Palladium GBP/toz", "unit": "GBP", "icon": "mdi:currency-gbp"},
    {"name": "Palladium GBP/g", "unit": "GBP", "icon": "mdi:currency-gbp"},
    {"name": "Palladium GBP/kg", "unit": "GBP", "icon": "mdi:currency-gbp"},
    {"name": "Palladium CHF/toz", "unit": "CHF", "icon": "mdi:currency-fra"},
    {"name": "Palladium CHF/g", "unit": "CHF", "icon": "mdi:currency-fra"},
    {"name": "Palladium CHF/kg", "unit": "CHF", "icon": "mdi:currency-fra"},
]


class MetalPriceCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetches metal prices every 5 minutes (source update frequency)."""

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="precious_metal_prices_metals",
            update_interval=METAL_SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, Any] | None:
        """Fetch metal API and currency API once; return combined data.
        Called once per SCAN_INTERVAL by the coordinator. Result is stored
        in coordinator.data and used by all PreciousMetalSensor entities.
        """
        session = async_get_clientsession(self.hass)
        t0 = time.monotonic()
        try:
            """timeout to allow to get out
            If either API is slow to respond, the request can hang indefinitely
            causing HA to log an error when the connection eventually drops.
            """
            async with session.get(METAL_API_URL, timeout=10) as resp:
                resp.raise_for_status()
                price_data = await resp.json()

                # Validate response is not empty and contains required fields
                if not price_data or not isinstance(price_data, dict):
                    _LOGGER.warning(
                        "Metal API returned invalid data: empty or non-dict response"
                    )
                    return None

                missing_fields = REQUIRED_METAL_FIELDS - set(price_data.keys())
                if missing_fields:
                    _LOGGER.warning(
                        "Metal API response missing required fields: %s",
                        missing_fields,
                    )
                    return None

                _LOGGER.debug(
                    "Metal API updated in %.2fs", time.monotonic() - t0
                )
                return price_data

        except Exception as err:
            _LOGGER.warning("Metal API request failed: %s", err)
            return None


class CurrencyCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetches EUR-GBP/CHF rates once per hours."""

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="precious_metal_prices_currency",
            update_interval=CURRENCY_SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, float | None]:
        session = async_get_clientsession(self.hass)
        t0 = time.monotonic()
        try:
            async with session.get(CURRENCY_API_URL, timeout=10) as resp:
                resp.raise_for_status()
                currency_data = await resp.json(content_type=None)

                # Validate currency data structure
                if not currency_data or not isinstance(currency_data, dict):
                    raise ValueError("Currency API returned empty or non-dict response")

                eur_data = currency_data.get("eur")
                if not isinstance(eur_data, dict):
                    raise ValueError("Currency API missing 'eur' key in response")

                if "gbp" not in eur_data or "chf" not in eur_data:
                    raise ValueError("Currency API missing 'gbp' or 'chf' in eur data")

                rates = {
                    "gbp_rate": float(eur_data["gbp"]),
                    "chf_rate": float(eur_data["chf"]),
                }
                _LOGGER.debug(
                    "Currency API updated in %.2fs (GBP=%.4f, CHF=%.4f)",
                    time.monotonic() - t0,
                    rates["gbp_rate"],
                    rates["chf_rate"],
                )
                return rates

        except Exception as err:
            _LOGGER.warning(
                "Currency API request failed: %s. USD/EUR sensors still work; "
                "GBP/CHF or other currency sensors will use last. "
                "Check network/DNS/firewall to latest.currency-api.pages.dev",
                err,
            )
            _LOGGER.debug("Currency API full error", exc_info=True)
            # Return None to keep last known data (coordinator preserves previous data on failure)
            return None

async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities) -> None:
    """Set up sensors from the two coordinators (created in __init__.py)."""
    metal_coordinator: MetalPriceCoordinator = hass.data[DOMAIN][entry.entry_id]["metal"]
    currency_coordinator: CurrencyCoordinator = hass.data[DOMAIN][entry.entry_id]["currency"]

    sensors = [
        PreciousMetalSensor(
            cfg["name"], cfg["unit"], cfg["icon"],
            metal_coordinator, currency_coordinator
        )
        for cfg in SENSORS
    ]

    async_add_entities(sensors, update_before_add=True)


class PreciousMetalSensor(CoordinatorEntity[MetalPriceCoordinator], SensorEntity):
    """Sensor that reads from coordinators data.

    should_poll = False so Home Assistant does not call update() on each entity every scan.
    Instead we rely on _handle_coordinator_update when the coordinator refreshes.
    Subscribes to metal_coordinator for updates (drives the refresh cycle).
    Reads currency rates from currency_coordinator.data directly (no re-fetch).
    """

    _attr_should_poll = False
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        name: str,
        unit: str,
        icon: str,
        metal_coordinator: MetalPriceCoordinator,
        currency_coordinator: CurrencyCoordinator,
    ) -> None:
        super().__init__(metal_coordinator)
        self._currency_coordinator = currency_coordinator
        self._attr_name = name
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit
        self._attr_unique_id = name.lower().replace(" ", "_")
        self._attr_native_value = None

    # check if we have value or put a 0.0 as default.
    def _get_rates(self) -> tuple[float, float]:
        data = self._currency_coordinator.data or {}
        return float(data.get("gbp_rate", 0.0)), float(data.get("chf_rate", 0.0))

    def _update_from_coordinator_data(self) -> None:
        """Derive this sensor's value from coordinators data."""
        data = self.coordinator.data
        if data is None:
            self._attr_native_value = None
            return

        gbp_rate, chf_rate = self._get_rates()

        try:
            # Update using elif to limit the unusefull comparisons.
            n = self._attr_name
            # Gold
            if n == "Gold USD/toz":
                self._attr_native_value = round(float(data["gold_usd"]), 2)
            elif n == "Gold USD/g":
                self._attr_native_value = round(float(data["gold_usd"]) / 31.1, 2)
            elif n == "Gold USD/kg":
                self._attr_native_value = round(float(data["gold_usd"]) / 31.1 * 1000, 2)
            elif n == "Gold EUR/toz":
                self._attr_native_value = round(float(data["gold_eur"]), 2)
            elif n == "Gold EUR/g":
                self._attr_native_value = round(float(data["gold_eur"]) / 31.1, 2)
            elif n == "Gold EUR/kg":
                self._attr_native_value = round(float(data["gold_eur"]) / 31.1 * 1000, 2)
            elif n == "Gold GBP/toz":
                self._attr_native_value = round(float(data["gold_eur"]) * gbp_rate, 2)
            elif n == "Gold GBP/g":
                self._attr_native_value = round(float(data["gold_eur"]) / 31.1 * gbp_rate, 2)
            elif n == "Gold GBP/kg":
                self._attr_native_value = round(float(data["gold_eur"]) / 31.1 * 1000 * gbp_rate, 2)
            elif n == "Gold CHF/toz":
                self._attr_native_value = round(float(data["gold_eur"]) * chf_rate, 2)
            elif n == "Gold CHF/g":
                self._attr_native_value = round(float(data["gold_eur"]) / 31.1 * chf_rate, 2)
            elif n == "Gold CHF/kg":
                self._attr_native_value = round(float(data["gold_eur"]) / 31.1 * 1000 * chf_rate, 2)
            # Silver
            elif n == "Silver USD/toz":
                self._attr_native_value = round(float(data["silber_usd"]), 2)
            elif n == "Silver USD/g":
                self._attr_native_value = round(float(data["silber_usd"]) / 31.1, 2)
            elif n == "Silver USD/kg":
                self._attr_native_value = round(float(data["silber_usd"]) / 31.1 * 1000, 2)
            elif n == "Silver EUR/toz":
                self._attr_native_value = round(float(data["silber_eur"]), 2)
            elif n == "Silver EUR/g":
                self._attr_native_value = round(float(data["silber_eur"]) / 31.1, 2)
            elif n == "Silver EUR/kg":
                self._attr_native_value = round(float(data["silber_eur"]) / 31.1 * 1000, 2)
            elif n == "Silver GBP/toz":
                self._attr_native_value = round(float(data["silber_eur"]) * gbp_rate, 2)
            elif n == "Silver GBP/g":
                self._attr_native_value = round(float(data["silber_eur"]) / 31.1 * gbp_rate, 2)
            elif n == "Silver GBP/kg":
                self._attr_native_value = round(float(data["silber_eur"]) / 31.1 * 1000 * gbp_rate, 2)
            elif n == "Silver CHF/toz":
                self._attr_native_value = round(float(data["silber_eur"]) * chf_rate, 2)
            elif n == "Silver CHF/g":
                self._attr_native_value = round(float(data["silber_eur"]) / 31.1 * chf_rate, 2)
            elif n == "Silver CHF/kg":
                self._attr_native_value = round(float(data["silber_eur"]) / 31.1 * 1000 * chf_rate, 2)
            # Platinum
            elif n == "Platinum USD/toz":
                self._attr_native_value = round(float(data["platin_usd"]), 2)
            elif n == "Platinum USD/g":
                self._attr_native_value = round(float(data["platin_usd"]) / 31.1, 2)
            elif n == "Platinum USD/kg":
                self._attr_native_value = round(float(data["platin_usd"]) / 31.1 * 1000, 2)
            elif n == "Platinum EUR/toz":
                self._attr_native_value = round(float(data["platin_eur"]), 2)
            elif n == "Platinum EUR/g":
                self._attr_native_value = round(float(data["platin_eur"]) / 31.1, 2)
            elif n == "Platinum EUR/kg":
                self._attr_native_value = round(float(data["platin_eur"]) / 31.1 * 1000, 2)
            elif n == "Platinum GBP/toz":
                self._attr_native_value = round(float(data["platin_eur"]) * gbp_rate, 2)
            elif n == "Platinum GBP/g":
                self._attr_native_value = round(float(data["platin_eur"]) / 31.1 * gbp_rate, 2)
            elif n == "Platinum GBP/kg":
                self._attr_native_value = round(float(data["platin_eur"]) / 31.1 * 1000 * gbp_rate, 2)
            elif n == "Platinum CHF/toz":
                self._attr_native_value = round(float(data["platin_eur"]) * chf_rate, 2)
            elif n == "Platinum CHF/g":
                self._attr_native_value = round(float(data["platin_eur"]) / 31.1 * chf_rate, 2)
            elif n == "Platinum CHF/kg":
                self._attr_native_value = round(float(data["platin_eur"]) / 31.1 * 1000 * chf_rate, 2)
            # Palladium
            elif n == "Palladium USD/toz":
                self._attr_native_value = round(float(data["palladium_usd"]), 2)
            elif n == "Palladium USD/g":
                self._attr_native_value = round(float(data["palladium_usd"]) / 31.1, 2)
            elif n == "Palladium USD/kg":
                self._attr_native_value = round(float(data["palladium_usd"]) / 31.1 * 1000, 2)
            elif n == "Palladium EUR/toz":
                self._attr_native_value = round(float(data["palladium_eur"]), 2)
            elif n == "Palladium EUR/g":
                self._attr_native_value = round(float(data["palladium_eur"]) / 31.1, 2)
            elif n == "Palladium EUR/kg":
                self._attr_native_value = round(float(data["palladium_eur"]) / 31.1 * 1000, 2)
            elif n == "Palladium GBP/toz":
                self._attr_native_value = round(float(data["palladium_eur"]) * gbp_rate, 2)
            elif n == "Palladium GBP/g":
                self._attr_native_value = round(float(data["palladium_eur"]) / 31.1 * gbp_rate, 2)
            elif n == "Palladium GBP/kg":
                self._attr_native_value = round(float(data["palladium_eur"]) / 31.1 * 1000 * gbp_rate, 2)
            elif n == "Palladium CHF/toz":
                self._attr_native_value = round(float(data["palladium_eur"]) * chf_rate, 2)
            elif n == "Palladium CHF/g":
                self._attr_native_value = round(float(data["palladium_eur"]) / 31.1 * chf_rate, 2)
            elif n == "Palladium CHF/kg":
                self._attr_native_value = round(float(data["palladium_eur"]) / 31.1 * 1000 * chf_rate, 2)

        except KeyError as err:
            _LOGGER.warning(
                "Missing field %s in API response. Sensor %s cannot be updated.",
                err,
                self._attr_name,
            )
            self._attr_native_value = None
        except (ValueError, TypeError) as err:
            _LOGGER.warning(
                "Invalid data type in API response for sensor %s: %s",
                self._attr_name,
                err,
            )
            self._attr_native_value = None

        _LOGGER.debug(
            "%s updated to %s %s",
            self._attr_name,
            self._attr_native_value,
            self._attr_native_unit_of_measurement,
        )

    def _handle_coordinator_update(self) -> None:
        """Called when metal coordinator has new data"""
        self._update_from_coordinator_data()
        self.async_write_ha_state()
