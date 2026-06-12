from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, ROBOT_STATE_MAP, STOP_REASON_MAP
from .coordinator import RobomowCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: RobomowCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            RobomowBatterySensor(coordinator, entry),
            RobomowActivitySensor(coordinator, entry),
            RobomowStopReasonSensor(coordinator, entry),
            RobomowStateSensor(coordinator, entry),
        ]
    )


class _RobomowEntity(CoordinatorEntity[RobomowCoordinator]):
    def __init__(self, coordinator: RobomowCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._device_id = coordinator.device_id

    @property
    def device_info(self) -> DeviceInfo:
        return DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name="Robomow",
            manufacturer="Robomow",
            model=self._device_id,
        )


class RobomowBatterySensor(_RobomowEntity, SensorEntity):
    _attr_device_class             = SensorDeviceClass.BATTERY
    _attr_state_class              = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "%"

    @property
    def unique_id(self) -> str:
        return f"robomow_{self._device_id}_battery"

    @property
    def name(self) -> str:
        return "Robomow Battery"

    @property
    def native_value(self) -> int | None:
        data = self.coordinator.data
        if data:
            return data.get("batteryInfo", {}).get("percent")
        return None


class RobomowActivitySensor(_RobomowEntity, SensorEntity):
    _attr_icon = "mdi:robot-mower"

    @property
    def unique_id(self) -> str:
        return f"robomow_{self._device_id}_activity"

    @property
    def name(self) -> str:
        return "Robomow Activity"

    @property
    def native_value(self) -> str | None:
        data = self.coordinator.data
        if data is None:
            return None
        state = data.get("state")
        if state is None:
            return None
        return ROBOT_STATE_MAP.get(state, f"Unknown ({state})")


class RobomowStopReasonSensor(_RobomowEntity, SensorEntity):
    _attr_icon = "mdi:alert-circle-outline"

    @property
    def unique_id(self) -> str:
        return f"robomow_{self._device_id}_stop_reason"

    @property
    def name(self) -> str:
        return "Robomow Stop Reason"

    @property
    def native_value(self) -> str | None:
        data = self.coordinator.data
        if data is None:
            return None
        # stopReason lives inside the current (or most recent previous) operation.
        for key in ("currentOperation", "previousOperation"):
            op = (data.get("operations") or {}).get(key)
            if op:
                sr = (op.get("info") or {}).get("stopReason")
                if sr is not None:
                    code = sr.get("id")
                    if code is not None:
                        return STOP_REASON_MAP.get(code, f"Unknown ({code})")
        return None


class RobomowStateSensor(_RobomowEntity, SensorEntity):
    _attr_icon            = "mdi:information-outline"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def unique_id(self) -> str:
        return f"robomow_{self._device_id}_robot_state"

    @property
    def name(self) -> str:
        return "Robomow Robot State"

    @property
    def native_value(self) -> int | None:
        data = self.coordinator.data
        return data.get("state") if data else None
