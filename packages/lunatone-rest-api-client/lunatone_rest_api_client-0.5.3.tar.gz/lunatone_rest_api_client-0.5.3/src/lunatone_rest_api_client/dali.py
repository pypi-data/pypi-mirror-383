from typing import ClassVar

from lunatone_rest_api_client import Auth
from lunatone_rest_api_client.base import Controllable
from lunatone_rest_api_client.models import (
    ControlData,
    ScanData,
    ScanState,
    StartScanData,
)


class DALIScan:
    """Class that represents a DALI Scan object in the API."""

    path: ClassVar[str] = "dali/scan"

    def __init__(self, auth: Auth) -> None:
        self._auth = auth
        self._data = ScanData()

    @property
    def data(self) -> ScanData:
        """Return the raw scan data."""
        return self._data

    @property
    def status(self) -> ScanState:
        """Return the scan status."""
        return self.data.status

    @property
    def is_busy(self) -> bool:
        """Return if the scan is in progress."""
        return (
            self.status == ScanState.ADDRESSING or self.status == ScanState.IN_PROGRESS
        )

    @property
    def progress(self) -> float:
        """Return a progress value in percent."""
        return self.data.progress if self.data.progress is not None else 0.0

    async def async_update(self) -> None:
        """Update the DALI scan."""
        response = await self._auth.get(self.path)
        self._data = ScanData.model_validate(await response.json())

    async def async_start(self, data: StartScanData) -> None:
        """Start the DALI scan."""
        json_data = data.model_dump(by_alias=True, exclude_none=True)
        response = await self._auth.post(self.path, json=json_data)
        self._data = ScanData.model_validate(await response.json())

    async def async_cancel(self) -> None:
        """Cancel the DALI scan."""
        response = await self._auth.post(f"{self.path}/cancel")
        self._data = ScanData.model_validate(await response.json())


class DALIBroadcast(Controllable):
    """Class that represents a DALI broadcast object in the API."""

    path: ClassVar[str] = "broadcast"

    def __init__(self, auth: Auth, line: int | None = None) -> None:
        self._auth = auth
        self._line = line

    @property
    def line(self) -> int | None:
        """Return the DALI line number."""
        return self._line

    async def async_control(self, data: ControlData) -> None:
        """Control the DALI broadcast."""
        json_data = data.model_dump(by_alias=True, exclude_none=True)
        await self._auth.post(
            f"{self.path}/control",
            json=json_data,
            params={"_line": self.line} if self.line is not None else None,
        )


class DALIGroup(Controllable):
    """Class that represents a DALI group object in the API."""

    path: ClassVar[str] = "group"

    def __init__(self, auth: Auth, group_number: int, line: int | None = None) -> None:
        self._auth = auth
        self._line = line
        self._number = group_number

    @property
    def line(self) -> int | None:
        """Return the DALI line number."""
        return self._line

    @property
    def number(self) -> int:
        """Return the DALI group number."""
        return self._number

    async def async_control(self, data: ControlData) -> None:
        """Control the DALI group."""
        json_data = data.model_dump(by_alias=True, exclude_none=True)
        await self._auth.post(
            f"{self.path}/{self.number}/control",
            json=json_data,
            params={"_line": self.line} if self.line is not None else None,
        )
