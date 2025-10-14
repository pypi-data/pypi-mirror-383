"""Helpers for the embodyserial interface."""

import logging
import struct
import time
from datetime import datetime
from datetime import UTC

from embodycodec import attributes
from embodycodec import codec
from embodycodec import types
from serial.serialutil import SerialException

from embodyserial.embodyserial import EmbodySender
from embodyserial.exceptions import MissingResponseError
from embodyserial.exceptions import NackError

logger = logging.getLogger(__name__)


class EmbodySendHelper:
    """Facade to make send/receive more protocol agnostic with simple get/set methods."""

    def __init__(self, sender: EmbodySender, timeout: int | None = 30) -> None:
        self.__sender = sender
        self.__send_timeout = timeout

    def get_current_time(self) -> datetime:
        response_attribute = self.__do_send_get_attribute_request(attributes.CurrentTimeAttribute.attribute_id)
        return datetime.fromtimestamp(response_attribute.value / 1000, tz=UTC)

    def get_serial_no(self) -> str:
        response_attribute = self.__do_send_get_attribute_request(attributes.SerialNoAttribute.attribute_id)
        response = response_attribute.formatted_value()
        if response is None:
            raise ValueError("Serial number not available")
        return response

    def get_vendor(self) -> str:
        response_attribute = self.__do_send_get_attribute_request(attributes.VendorAttribute.attribute_id)
        response = response_attribute.formatted_value()
        if response is None:
            raise ValueError("Vendor information not available")
        return response

    def get_model(self) -> str:
        response_attribute = self.__do_send_get_attribute_request(attributes.ModelAttribute.attribute_id)
        response = response_attribute.formatted_value()
        if response is None:
            raise ValueError("Model information not available")
        return response

    def get_bluetooth_mac(self) -> str:
        response_attribute = self.__do_send_get_attribute_request(attributes.BluetoothMacAttribute.attribute_id)
        response = response_attribute.formatted_value()
        if response is None:
            raise ValueError("Bluetooth MAC address not available")
        return response

    def get_battery_level(self) -> int:
        response_attribute = self.__do_send_get_attribute_request(attributes.BatteryLevelAttribute.attribute_id)
        return response_attribute.value

    def get_heart_rate(self) -> int:
        response_attribute = self.__do_send_get_attribute_request(attributes.HeartrateAttribute.attribute_id)
        return response_attribute.value

    def get_charge_state(self) -> bool:
        response_attribute = self.__do_send_get_attribute_request(attributes.ChargeStateAttribute.attribute_id)
        return response_attribute.value

    def get_temperature(self) -> float:
        response_attribute = self.__do_send_get_attribute_request(attributes.TemperatureAttribute.attribute_id)
        if not isinstance(response_attribute, attributes.TemperatureAttribute):
            raise TypeError(f"Expected TemperatureAttribute, got {type(response_attribute).__name__}")
        return response_attribute.temp_celsius()

    def get_firmware_version(self) -> str:
        response_attribute = self.__do_send_get_attribute_request(attributes.FirmwareVersionAttribute.attribute_id)
        response = response_attribute.formatted_value()
        if response is None:
            raise ValueError("Firmware version not available")
        return response

    def get_on_body_state(self) -> bool:
        response_attribute = self.__do_send_get_attribute_request(attributes.BeltOnBodyStateAttribute.attribute_id)
        return response_attribute.value

    def get_recording_state(self) -> bool:
        """Name of attribute makes no sence but is correct..."""
        response_attribute = self.__do_send_get_attribute_request(
            attributes.MeasurementDeactivatedAttribute.attribute_id
        )
        return response_attribute.value

    def get_files(self) -> list[tuple[str, int]]:
        """Get a list of tuples with file name and file size."""
        response = self.__sender.send(msg=codec.ListFiles(), timeout=120)
        if not response:
            raise MissingResponseError
        if isinstance(response, codec.NackResponse):
            raise NackError(response)
        if not isinstance(response, codec.ListFilesResponse):
            raise TypeError(f"Expected ListFilesResponse, got {type(response).__name__}")

        files: list[tuple[str, int]] = []
        if len(response.files) == 0:
            return files
        else:
            for file in response.files:
                files.append((str(file.file_name), file.file_size))
            return files

    def delete_file(self, file_name: str) -> bool:
        response = self.__sender.send(msg=codec.DeleteFile(types.File(file_name)), timeout=self.__send_timeout)
        if not response:
            raise MissingResponseError()
        if isinstance(response, codec.NackResponse):
            raise NackError(response)
        if not isinstance(response, codec.DeleteFileResponse):
            raise TypeError(f"Expected DeleteFileResponse, got {type(response).__name__}")
        return True

    def delete_file_with_retries(self, file_name: str, retries=3, timeout_seconds_per_retry=0.5) -> bool:
        for retry in range(1, retries + 1):
            try:
                if self.delete_file(file_name):
                    logger.info(f"Deleted file on device: {file_name}")
                    return True
                logger.warning(f"Delete failed for {file_name} (attempt: {retry})")
                time.sleep(timeout_seconds_per_retry)
                continue
            except (MissingResponseError, NackError, SerialException) as e:
                logger.warning(f"Delete failed for {file_name} (attempt: {retry}): {e}")
                time.sleep(timeout_seconds_per_retry)
                continue
        return False

    def set_current_timestamp(self) -> bool:
        return self.set_timestamp(datetime.now(UTC))

    def set_timestamp(self, time: datetime) -> bool:
        attr = attributes.CurrentTimeAttribute(int(time.timestamp() * 1000))
        return self.__do_send_set_attribute_request(attr)

    def set_trace_level(self, level: int) -> bool:
        attr = attributes.TraceLevelAttribute(level)
        return self.__do_send_set_attribute_request(attr)

    def reformat_disk(self) -> bool:
        response = self.__sender.send(msg=codec.ReformatDisk(), timeout=self.__send_timeout)
        if not response:
            raise MissingResponseError()
        if isinstance(response, codec.NackResponse):
            raise NackError(response)
        if not isinstance(response, codec.ReformatDiskResponse):
            raise TypeError(f"Expected ReformatDiskResponse, got {type(response).__name__}")
        return True

    def reset_device(self) -> bool:
        self.__sender.send_async(msg=codec.ExecuteCommand(command_id=codec.ExecuteCommand.RESET_DEVICE, value=b""))
        return True

    def reboot_device(self) -> bool:
        self.__sender.send_async(msg=codec.ExecuteCommand(command_id=codec.ExecuteCommand.REBOOT_DEVICE, value=b""))
        return True

    def click_button(self, click_count: int, click_duration_ms: int) -> bool:
        self.__sender.send_async(
            msg=codec.ExecuteCommand(
                command_id=types.ExecuteCommandType.PRESS_BUTTON.value,
                value=struct.pack(">BH", click_count, click_duration_ms),
            )
        )
        return True

    def delete_all_files(self) -> bool:
        response = self.__sender.send(msg=codec.DeleteAllFiles(), timeout=self.__send_timeout)
        if not response:
            raise MissingResponseError()
        if isinstance(response, codec.NackResponse):
            raise NackError(response)
        if not isinstance(response, codec.DeleteAllFilesResponse):
            raise TypeError(f"Expected DeleteAllFilesResponse, got {type(response).__name__}")
        return True

    def set_on_body_detect(self, enable: bool) -> bool:
        attr = attributes.OnBodyDetectAttribute(enable)
        return self.__do_send_set_attribute_request(attr)

    def get_on_body_detect(self) -> bool:
        response_attribute = self.__do_send_get_attribute_request(attributes.OnBodyDetectAttribute.attribute_id)
        return response_attribute.value

    def __do_send_get_attribute_request(self, attribute_id: int) -> attributes.Attribute:
        response = self.__sender.send(msg=codec.GetAttribute(attribute_id), timeout=self.__send_timeout)
        if not response:
            raise MissingResponseError()
        if isinstance(response, codec.NackResponse):
            raise NackError(response)
        if not isinstance(response, codec.GetAttributeResponse):
            raise TypeError(f"Expected GetAttributeResponse, got {type(response).__name__}")
        return response.value

    def __do_send_set_attribute_request(self, attr: attributes.Attribute) -> bool:
        response = self.__sender.send(
            msg=codec.SetAttribute(attribute_id=attr.attribute_id, value=attr),
            timeout=self.__send_timeout,
        )
        if not response:
            raise MissingResponseError()
        if isinstance(response, codec.NackResponse):
            raise NackError(response)
        return isinstance(response, codec.SetAttributeResponse)
