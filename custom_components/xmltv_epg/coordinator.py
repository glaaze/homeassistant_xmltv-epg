"""DataUpdateCoordinator for xmltv_epg."""
from __future__ import annotations

from datetime import datetime, timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import (
    XMLTVClient,
    XMLTVClientError,
)
from .const import DOMAIN, LOGGER, SENSOR_REFRESH_INTERVAL


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class XMLTVDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from XMLTV."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: XMLTVClient,
        update_interval: int,
        lookahead: int,
    ) -> None:
        """Initialize."""
        self.client = client
        self._lookahead = timedelta(minutes=lookahead)
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=SENSOR_REFRESH_INTERVAL),
        )

        self._guide = None
        self._last_refetch_time = None
        self._refetch_interval = timedelta(hours=update_interval)

    async def _refetch_tv_guide(self):
        """Re-fetch TV guide data."""
        try:
            guide = await self.client.async_get_data()
            LOGGER.debug(f"Updated XMLTV guide /w {len(guide.channels)} channels and {len(guide.programs)} programs.")

            self._guide = guide
            self._last_refetch_time = datetime.now()
        except XMLTVClientError as exception:
            raise UpdateFailed(exception) from exception

    def _should_refetch(self) -> bool:
        """Check if data should be refetched?."""
        # no guide data yet ?
        if not self._guide or not self._last_refetch_time:
            return True

        # check if refetch interval has passed
        next_refetch_time = self._last_refetch_time + self._refetch_interval
        return datetime.now() >= next_refetch_time

    async def _async_update_data(self):
        """Update data from cache or re-fetch if cache is expired."""
        if self._should_refetch():
            await self._refetch_tv_guide()

        return self._guide

    def get_current_time(self) -> datetime:
        """Get effective current time."""
        return datetime.now() + self._lookahead

    @property
    def last_update_time(self) -> datetime:
        """Get last update time."""
        return self._last_refetch_time
