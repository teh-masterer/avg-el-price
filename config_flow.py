import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_ENTITY_ID

DOMAIN = "avg_el_price"

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_ENTITY_ID): str,
})

class AverageEnergyPriceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for the Average Energy Price integration."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Average Energy Price", data=user_input)
        return self.async_show_form(step_id="user", data_schema=DATA_SCHEMA)
