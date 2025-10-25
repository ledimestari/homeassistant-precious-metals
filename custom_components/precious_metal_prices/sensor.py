"""Sensor platform for Precious Metal Prices."""

from __future__ import annotations

import logging

import requests
from homeassistant.components.sensor import SensorEntity

_LOGGER = logging.getLogger(__name__)

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
]


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up sensors."""
    sensors = [
        PreciousMetalSensor(cfg["name"], cfg["unit"], cfg["icon"]) for cfg in SENSORS
    ]
    async_add_entities(sensors, update_before_add=True)


class PreciousMetalSensor(SensorEntity):
    """Get values and update the sensors."""

    _attr_should_poll = True

    def __init__(self, name: str, unit: str, icon: str):
        self._attr_name = name
        self._attr_icon = icon
        self._attr_native_unit_of_measurement = unit
        self._attr_unique_id = name.lower().replace(" ", "_")
        self._attr_native_value = None

    def update(self):
        """Fetch updated metal price data."""
        try:
            # Get metal price data
            url = "https://api.edelmetalle.de/public.json"
            price_response = requests.get(url)
            price_data = price_response.json()

            # Get gbp conversion rates, eur to gbp
            url = "https://latest.currency-api.pages.dev/v1/currencies/eur.json"
            currency_response = requests.get(url)
            currency_data = currency_response.json()
            gbp_rate = float(currency_data["eur"]["gbp"])

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
        except:  # noqa: E722 # Silence the linter as all errors here can be skipped
            # If json data is not valid, do nothing
            _LOGGER.info("Precious Metal Prices received invalid json data")

        _LOGGER.debug(
            "%s updated to %s %s",
            self._attr_name,
            self._attr_native_value,
            self._attr_native_unit_of_measurement,
        )
