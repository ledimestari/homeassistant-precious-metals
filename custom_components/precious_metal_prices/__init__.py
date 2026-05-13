"""Initialize Precious Metal Prices integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .sensor import CurrencyCoordinator, MetalPriceCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict):
    """Legacy YAML setup (not used)."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up integration from config entry."""
    _LOGGER.info("Setting up Precious Metal Prices integration")

    hass.data.setdefault(DOMAIN, {})

    # Distincitive coordinator to allow different update time.
    metal_coordinator = MetalPriceCoordinator(hass)
    currency_coordinator = CurrencyCoordinator(hass)
    
    # Fetch initial data before setting up sensors
    # Currency coordinator is refreshed first so rates are available immediately
    # when the metal coordinator triggers the first sensor update
    await currency_coordinator.async_config_entry_first_refresh()
    await metal_coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "metal": metal_coordinator,
        "currency": currency_coordinator,
    }

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    _LOGGER.info("Unloading Precious Metal Prices integration")
    if await hass.config_entries.async_unload_platforms(entry, ["sensor"]):
        hass.data[DOMAIN].pop(entry.entry_id, None)
        return True
    return False
