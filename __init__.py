"""The avg-el-price integration."""
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

DOMAIN = "avg_el_price"

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the avg-el-price component."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up avg-el-price from a config entry."""
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entry.data
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(entry, "sensor")
    )
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload avg-el-price config entry."""
    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
