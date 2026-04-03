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
SCAN_INTERVAL = timedelta(seconds=60)

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


class PreciousMetalCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetches metal prices and EUR→GBP rate once per update interval.

    All sensors read from coordinator.data.
    """

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="precious_metal_prices",
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, Any] | None:
        """Fetch metal API and currency API once; return combined data.

        Called once per SCAN_INTERVAL by the coordinator. Result is stored
        in coordinator.data and used by all PreciousMetalSensor entities.
        """
        session = async_get_clientsession(self.hass)
        result: dict[str, Any] = {}
        t0 = time.monotonic()
        api_calls = 0

        try:
            async with session.get(METAL_API_URL) as resp:
                resp.raise_for_status()
                price_data = await resp.json()
                result.update(price_data)
            api_calls += 1
            _LOGGER.debug(
                "Metal API call 1/2 completed in %.2fs",
                time.monotonic() - t0,
            )
        except Exception as err:
            _LOGGER.warning("Metal API request failed: %s", err)
            return result if result else None

        try:
            t1 = time.monotonic()
            async with session.get(CURRENCY_API_URL) as resp:
                resp.raise_for_status()
                currency_data = await resp.json()
                result["gbp_rate"] = float(currency_data["eur"]["gbp"])
                result["chf_rate"] = float(currency_data["eur"]["chf"])
            api_calls += 1
            _LOGGER.debug(
                "Currency API call 2/2 completed in %.2fs (total so far: %.2fs)",
                time.monotonic() - t1,
                time.monotonic() - t0,
            )
        except Exception as err:
            _LOGGER.warning(
                "Currency API request failed: %s. USD/EUR sensors still work; "
                "GBP sensors will be unavailable. Check network/DNS/firewall to "
                "latest.currency-api.pages.dev",
                err,
            )
            _LOGGER.debug("Currency API full error", exc_info=True)
            if not result:
                return None
            result["gbp_rate"] = None

        total_elapsed = time.monotonic() - t0
        _LOGGER.debug(
            "Precious metal refresh: %d API calls, %.2fs total",
            api_calls,
            total_elapsed,
        )
        return result


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensors from the shared coordinator (created in __init__.py)."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    sensors = [
        PreciousMetalSensor(cfg["name"], cfg["unit"], cfg["icon"], coordinator)
        for cfg in SENSORS
    ]
    async_add_entities(sensors, update_before_add=True)


class PreciousMetalSensor(CoordinatorEntity[PreciousMetalCoordinator], SensorEntity):
    """Sensor that reads from coordinator data.

    should_poll = False so Home Assistant does not call update() on each
    entity every scan. Instead we rely
    on _handle_coordinator_update when the coordinator refreshes.
    """

    _attr_should_poll = False
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self,
        name: str,
        unit: str,
        icon: str,
        coordinator: PreciousMetalCoordinator,
    ) -> None:
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit
        self._attr_unique_id = name.lower().replace(" ", "_")
        self._attr_native_value = None

    def _update_from_coordinator_data(self) -> None:
        """Derive this sensor's value from shared coordinator.data."""
        data = self.coordinator.data
        if data is None:
            return
        price_data = data

        # check rate values
        gbp_rate = data.get("gbp_rate")
        if gbp_rate is None:
            gbp_rate = 0.0
        else:
            gbp_rate = float(gbp_rate)

        chf_rate = data.get("chf_rate")
        if chf_rate is None:
            chf_rate = 0.0
        else:
            chf_rate = float(chf_rate)

        try:
            # Update sensor values
            # ------
            # Gold
            # ---
            if self._attr_name == "Gold USD/toz":
                self._attr_native_value = round(float(price_data["gold_usd"]), 2)
            # ---
            if self._attr_name == "Gold USD/g":
                self._attr_native_value = round(float(price_data["gold_usd"]) / 31.1, 2)
            # ---
            if self._attr_name == "Gold USD/kg":
                self._attr_native_value = round(
                    float(price_data["gold_usd"]) / 31.1 * 1000, 2
                )
            # ---
            if self._attr_name == "Gold EUR/toz":
                self._attr_native_value = round(float(price_data["gold_eur"]), 2)
            # ---
            if self._attr_name == "Gold EUR/g":
                self._attr_native_value = round(float(price_data["gold_eur"]) / 31.1, 2)
            # ---
            if self._attr_name == "Gold EUR/kg":
                self._attr_native_value = round(
                    float(price_data["gold_eur"]) / 31.1 * 1000, 2
                )
            # ---
            if self._attr_name == "Gold GBP/toz":
                self._attr_native_value = round(
                    float(price_data["gold_eur"]) * gbp_rate, 2
                )
            # ---
            if self._attr_name == "Gold GBP/g":
                self._attr_native_value = round(
                    (float(price_data["gold_eur"]) / 31.1) * gbp_rate, 2
                )
            # ---
            if self._attr_name == "Gold GBP/kg":
                self._attr_native_value = round(
                    (float(price_data["gold_eur"]) / 31.1 * 1000) * gbp_rate, 2
                )
            # ---
            if self._attr_name == "Gold CHF/toz":
                self._attr_native_value = round(
                    float(price_data["gold_eur"]) * chf_rate, 2
                )
            # ---
            if self._attr_name == "Gold CHF/g":
                self._attr_native_value = round(
                    (float(price_data["gold_eur"]) / 31.1) * chf_rate, 2
                )
            # ---
            if self._attr_name == "Gold CHF/kg":
                self._attr_native_value = round(
                    (float(price_data["gold_eur"]) / 31.1 * 1000) * chf_rate, 2
                )
            # ------
            # Silver
            # ---
            if self._attr_name == "Silver USD/toz":
                self._attr_native_value = round(float(price_data["silber_usd"]), 2)
            # ---
            if self._attr_name == "Silver USD/g":
                self._attr_native_value = round(
                    float(price_data["silber_usd"]) / 31.1, 2
                )
            # ---
            if self._attr_name == "Silver USD/kg":
                self._attr_native_value = round(
                    float(price_data["silber_usd"]) / 31.1 * 1000, 2
                )
            # ---
            if self._attr_name == "Silver EUR/toz":
                self._attr_native_value = round(float(price_data["silber_eur"]), 2)
            # ---
            if self._attr_name == "Silver EUR/g":
                self._attr_native_value = round(
                    float(price_data["silber_eur"]) / 31.1, 2
                )
            # ---
            if self._attr_name == "Silver EUR/kg":
                self._attr_native_value = round(
                    float(price_data["silber_eur"]) / 31.1 * 1000, 2
                )
            # ---
            if self._attr_name == "Silver GBP/toz":
                self._attr_native_value = round(
                    float(price_data["silber_eur"]) * gbp_rate, 2
                )
            # ---
            if self._attr_name == "Silver GBP/g":
                self._attr_native_value = round(
                    (float(price_data["silber_eur"]) / 31.1) * gbp_rate, 2
                )
            # ---
            if self._attr_name == "Silver GBP/kg":
                self._attr_native_value = round(
                    (float(price_data["silber_eur"]) / 31.1 * 1000) * gbp_rate, 2
                )
            # ---
            if self._attr_name == "Silver CHF/toz":
                self._attr_native_value = round(
                    float(price_data["silber_eur"]) * chf_rate, 2
                )
            # ---
            if self._attr_name == "Silver CHF/g":
                self._attr_native_value = round(
                    (float(price_data["silber_eur"]) / 31.1) * chf_rate, 2
                )
            # ---
            if self._attr_name == "Silver CHF/kg":
                self._attr_native_value = round(
                    (float(price_data["silber_eur"]) / 31.1 * 1000) * chf_rate, 2
                )
            # ------
            # Platinum
            # ---
            if self._attr_name == "Platinum USD/toz":
                self._attr_native_value = round(float(price_data["platin_usd"]), 2)
            # ---
            if self._attr_name == "Platinum USD/g":
                self._attr_native_value = round(
                    float(price_data["platin_usd"]) / 31.1, 2
                )
            # ---
            if self._attr_name == "Platinum USD/kg":
                self._attr_native_value = round(
                    float(price_data["platin_usd"]) / 31.1 * 1000, 2
                )
            # ---
            if self._attr_name == "Platinum EUR/toz":
                self._attr_native_value = round(float(price_data["platin_eur"]), 2)
            # ---
            if self._attr_name == "Platinum EUR/g":
                self._attr_native_value = round(
                    float(price_data["platin_eur"]) / 31.1, 2
                )
            # ---
            if self._attr_name == "Platinum EUR/kg":
                self._attr_native_value = round(
                    float(price_data["platin_eur"]) / 31.1 * 1000, 2
                )
            # ---
            if self._attr_name == "Platinum GBP/toz":
                self._attr_native_value = round(
                    float(price_data["platin_eur"]) * gbp_rate, 2
                )
            # ---
            if self._attr_name == "Platinum GBP/g":
                self._attr_native_value = round(
                    (float(price_data["platin_eur"]) / 31.1) * gbp_rate, 2
                )
            # ---
            if self._attr_name == "Platinum GBP/kg":
                self._attr_native_value = round(
                    (float(price_data["platin_eur"]) / 31.1 * 1000) * gbp_rate, 2
                )
            # ---
            if self._attr_name == "Platinum CHF/toz":
                self._attr_native_value = round(
                    float(price_data["platin_eur"]) * chf_rate, 2
                )
            # ---
            if self._attr_name == "Platinum CHF/g":
                self._attr_native_value = round(
                    (float(price_data["platin_eur"]) / 31.1) * chf_rate, 2
                )
            # ---
            if self._attr_name == "Platinum CHF/kg":
                self._attr_native_value = round(
                    (float(price_data["platin_eur"]) / 31.1 * 1000) * chf_rate, 2
                )
            # ------
            # Palladium
            # ---
            if self._attr_name == "Palladium USD/toz":
                self._attr_native_value = round(float(price_data["palladium_usd"]), 2)
            # ---
            if self._attr_name == "Palladium USD/g":
                self._attr_native_value = round(
                    float(price_data["palladium_usd"]) / 31.1, 2
                )
            # ---
            if self._attr_name == "Palladium USD/kg":
                self._attr_native_value = round(
                    float(price_data["palladium_usd"]) / 31.1 * 1000, 2
                )
            # ---
            if self._attr_name == "Palladium EUR/toz":
                self._attr_native_value = round(float(price_data["palladium_eur"]), 2)
            # ---
            if self._attr_name == "Palladium EUR/g":
                self._attr_native_value = round(
                    float(price_data["palladium_eur"]) / 31.1, 2
                )
            # ---
            if self._attr_name == "Palladium EUR/kg":
                self._attr_native_value = round(
                    float(price_data["palladium_eur"]) / 31.1 * 1000, 2
                )
            # ---
            if self._attr_name == "Palladium GBP/toz":
                self._attr_native_value = round(
                    float(price_data["palladium_eur"]) * gbp_rate, 2
                )
            # ---
            if self._attr_name == "Palladium GBP/g":
                self._attr_native_value = round(
                    (float(price_data["palladium_eur"]) / 31.1) * gbp_rate, 2
                )
            # ---
            if self._attr_name == "Palladium GBP/kg":
                self._attr_native_value = round(
                    (float(price_data["palladium_eur"]) / 31.1 * 1000) * gbp_rate, 2
                )
            # ---
            if self._attr_name == "Palladium CHF/toz":
                self._attr_native_value = round(
                    float(price_data["palladium_eur"]) * chf_rate, 2
                )
            # ---
            if self._attr_name == "Palladium CHF/g":
                self._attr_native_value = round(
                    (float(price_data["palladium_eur"]) / 31.1) * chf_rate, 2
                )
            # ---
            if self._attr_name == "Palladium CHF/kg":
                self._attr_native_value = round(
                    (float(price_data["palladium_eur"]) / 31.1 * 1000) * chf_rate, 2
                )
            # ---
        except Exception:  # noqa: BLE001
            _LOGGER.info("Precious Metal Prices received invalid json data")

        _LOGGER.debug(
            "%s updated to %s %s",
            self._attr_name,
            self._attr_native_value,
            self._attr_native_unit_of_measurement,
        )

    def _handle_coordinator_update(self) -> None:
        """Called when the coordinator has new data; refresh this sensor's state."""
        self._update_from_coordinator_data()
        self.async_write_ha_state()
