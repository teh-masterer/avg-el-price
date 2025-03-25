import logging
import datetime
import re

from homeassistant.helpers.entity import Entity
from homeassistant.core import HomeAssistant
from homeassistant.components.recorder import history

_LOGGER = logging.getLogger(__name__)

def get_daily_average_from_states(states):
    """Group states by day and return the average of the values closest to 23:50 each day."""
    daily_values = []
    groups = {}
    for state in states:
        dt = state.last_updated.replace(tzinfo=None)
        day = dt.date()
        groups.setdefault(day, []).append(state)
    target_minutes = 23 * 60 + 50
    for day, state_list in groups.items():
        best_state = None
        best_diff = None
        for st in state_list:
            ts = st.last_updated.replace(tzinfo=None)
            minutes = ts.hour * 60 + ts.minute
            diff = abs(minutes - target_minutes)
            if best_diff is None or diff < best_diff:
                best_diff = diff
                best_state = st
        try:
            # Remove all whitespace to handle thousand separators.
            value_str = "".join(best_state.state.strip().split())
            num_str = re.search(r"[\d]+(?:[.,]\d+)?", value_str).group(0)
            if ',' in num_str and '.' not in num_str:
                num_str = num_str.replace(',', '.')
            value = float(num_str)
            daily_values.append(value)
        except Exception as e:
            _LOGGER.error("Failed to parse state %s: %s", best_state.state, e)
    if daily_values:
        return sum(daily_values) / len(daily_values)
    return None

class AverageEnergyPriceSensor(Entity):
    """Sensor that calculates the average energy price for the current month-to-date.
    
    It uses historical data from a linked price sensor (which updates frequently) to pick out
    the reading closest to 23:50 each day for the current month, averages them, and sets this as its state.
    It also computes the previous month's average and exposes it as an attribute.
    """
    def __init__(self, hass: HomeAssistant, linked_sensor: str):
        """
        Args:
            hass: Home Assistant instance.
            linked_sensor: The entity_id of the price sensor.
        """
        self.hass = hass
        self._linked_sensor = linked_sensor
        self._state = None
        self._attributes = {}
        self._attr_name = "Average Energy Price"
        self._attr_unique_id = "average_energy_price_sensor"
        self._attr_icon = "mdi:flash-outline"

    async def async_update(self):
        now = datetime.datetime.now()
        current_month_start = datetime.datetime(now.year, now.month, 1)
        # Determine previous month start and end.
        if now.month == 1:
            prev_month = 12
            prev_year = now.year - 1
        else:
            prev_month = now.month - 1
            prev_year = now.year
        previous_month_start = datetime.datetime(prev_year, prev_month, 1)
        previous_month_end = current_month_start

        current_states = await self.hass.async_add_executor_job(
            lambda: history.get_state_changes_during_period(
                self.hass, current_month_start, now, entity_id=self._linked_sensor
            )
        )
        previous_states = await self.hass.async_add_executor_job(
            lambda: history.get_state_changes_during_period(
                self.hass, previous_month_start, previous_month_end, entity_id=self._linked_sensor
            )
        )
        states_current = current_states.get(self._linked_sensor, [])
        states_previous = previous_states.get(self._linked_sensor, [])

        avg_current = get_daily_average_from_states(states_current)
        avg_previous = get_daily_average_from_states(states_previous)

        self._state = avg_current
        self._attributes = {
            "previous month average": round(avg_previous, 2) if avg_previous is not None else "unknown",
            "linked sensor": self._linked_sensor,
            "current_month_start": current_month_start.isoformat(),
            "current_period_end": now.isoformat(),
        }

    @property
    def state(self):
        return round(self._state, 2) if self._state is not None else "unknown"

    @property
    def extra_state_attributes(self):
        return self._attributes
