"""Config flow for Precious Metal Prices integration."""

from homeassistant import config_entries

from .const import DOMAIN, TITLE


class PreciousMetalPricesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow with no user input."""

    async def async_step_user(self, user_input=None):
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title=TITLE, data={})
