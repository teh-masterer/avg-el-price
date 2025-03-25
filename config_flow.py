import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_ENTITY_ID

DOMAIN = "avg_el_price"

DATA_SCHEMA = vol.Schema({
    vol.Required(CONF_ENTITY_ID, default="sensor.nordpool_kwh_no5_nok_3_10_025"): str,
})

class AverageEnergyPriceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Average Energy Price integration."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle a flow initiated by the user."""
        if user_input is not None:
            return self.async_create_entry(title="Average Energy Price", data=user_input)
        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            description_placeholders={
                "description": "Refer to sensor which holds average electricity price for your area. This integration creates an average price sensor based on historic price information."
            }
        )
