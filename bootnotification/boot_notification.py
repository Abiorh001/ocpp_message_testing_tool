import asyncio
import websockets
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call
from ocpp.v16.enums import RegistrationStatus
import jsonschema
from utils.logger import setup_logger
from .schema import boot_notification_response_schema
from core.config import Config

# Setup the logger
logging = setup_logger(__name__)


def positive_test(response: dict, test_title: str) -> None:
    try:
        # verify if any response is received
        assert response is not None, "No response received."
        # verify if the response status is accepted
        assert (
            response.status == RegistrationStatus.accepted
        ), "Test failed for required data."
        # Convert the response to a dictionary
        response_dict = {
            "status": response.status,
            "currentTime": response.current_time,
            "interval": response.interval,
        }
        # Validate the response against the OCPP JSON schema
        jsonschema.validate(
            instance=response_dict, schema=boot_notification_response_schema
        )
        # validate the response data types
        assert isinstance(
            response_dict.get("currentTime"), str
        ), "currentTime is not a string"
        assert isinstance(
            response_dict.get("interval"), int
        ), "interval is not an integer"
        assert response_dict.get("status") in [
            "Accepted",
            "Pending",
            "Rejected",
        ], "status is not valid"
        # log all the pass test
        logging.info(f"{test_title} test passed")
    except jsonschema.exceptions.ValidationError as e:
        logging.error(f"Boot Notification Response Schema validation error: {e}")
        logging.error(f"{test_title} test failed")
    except AssertionError as e:
        logging.error(f"Assertion error: {e}")
        logging.error(f"{test_title} test failed")


def negative_test(response: dict, test_title: str) -> None:
    try:
        # verify if any response is received
        assert response is None, "Response received for incomplete data."
        if response is not None:
            # verify if the response status is accepted
            assert (
                response.status == RegistrationStatus.rejected
            ), "Test failed for incomplete data."
            # Convert the response to a dictionary
            response_dict = {
                "status": response.status,
                "currentTime": response.current_time,
                "interval": response.interval,
            }
            # Validate the response against the OCPP JSON schema
            jsonschema.validate(
                instance=response_dict, schema=boot_notification_response_schema
            )
            # validate the response data types
            assert isinstance(
                response_dict.get("currentTime"), str
            ), "currentTime is not a string"
            assert isinstance(
                response_dict.get("interval"), int
            ), "interval is not an integer"
            assert response_dict.get("status") in [
                "Accepted",
                "Pending",
                "Rejected",
            ], "status is not valid"
        # log all the pass test
        logging.info(f"{test_title} test passed")
    except jsonschema.exceptions.ValidationError as e:
        logging.error(f"Boot Notification Response Schema validation error: {e}")
        logging.error(f"{test_title} test failed")
    except AssertionError as e:
        logging.error(f"Assertion error: {e}")
        logging.error(f"{test_title} test failed")


class BootNotificationTest(cp):

    async def send_boot_notification_required_payload(self):
        request = call.BootNotification(
            charge_point_model="Charge-Gridflow", charge_point_vendor="GridFlow"
        )
        response = await self.call(request)
        positive_test(response, "send boot notification required payload")

    async def send_boot_notification_required_partial_optional_payload(self):
        request = call.BootNotification(
            charge_point_model="Charge",
            charge_point_vendor="GridFlow",
            firmware_version="1.0.0",
        )
        response = await self.call(request)
        positive_test(
            response, "send boot notification required and partial optional payload"
        )

    async def send_boot_notification_required_optional_complete_payload(self):
        request = call.BootNotification(
            charge_point_model="Charge",
            charge_point_vendor="GridFlow",
            charge_box_serial_number="123456",
            charge_point_serial_number="123456",
            firmware_version="1.0.0",
            iccid="XXXXXXXXXXXXXXXXXXXX",
            imsi="123456789012345",
            meter_type="DBT NQC-AC",
            meter_serial_number="123456",
        )
        response = await self.call(request)
        positive_test(
            response, "send boot notification required and optional complete payload"
        )

    async def send_boot_notification_incomplete_required_payload(self):
        request = call.BootNotification(
            charge_point_model="Charge-Gridflow",
        )
        response = await self.call(request)
        negative_test(response, "send boot notification incomplete required payload")

    async def send_boot_notification_optional_only_payload(self):
        request = call.BootNotification(
            charge_box_serial_number="123456",
            charge_point_serial_number="123456",
            firmware_version="1.0.0",
            iccid="XXXXXXXXXXXXXXXXXXXX",
            imsi="123456789012345",
            meter_type="DBT NQC-AC",
            meter_serial_number="123456",
        )
        response = await self.call(request)
        negative_test(response, "send boot notification optional only payload")

    async def send_boot_notification_wrong_payload_data_type(self):
        request = call.BootNotification(
            charge_point_model=123,
            charge_point_vendor="GridFlow",
        )
        response = await self.call(request)
        negative_test(response, "send boot notification wrong payload data type")

    async def send_boot_notification_no_payload(self):
        request = call.BootNotification()
        response = await self.call(request)
        negative_test(response, "send boot notification no payload")

    async def send_boot_notification_over_max_length_payload(self):
        request = call.BootNotification(
            charge_point_model="Charge-Gridflow-Charge-Gridflow-Charge-Gridflow",
            charge_point_vendor="GridFlowCharge-GridflowCharge-GridflowCharge-Gridflow",
        )
        response = await self.call(request)
        return negative_test(response, "send boot notification over max length payload")


async def run_boot_notification():
    async with websockets.connect(
        Config.WEBSOCKET_URL + Config.CHARGE_POINT_ID, subprotocols=["ocpp1.6"]
    ) as ws:
        cp_id = Config.CHARGE_POINT_ID
        boot_notification_test = BootNotificationTest(cp_id, ws)

        try:
            await asyncio.wait_for(
                asyncio.gather(
                    boot_notification_test.start(),
                    boot_notification_test.send_boot_notification_required_payload(),
                    boot_notification_test.send_boot_notification_required_partial_optional_payload(),
                    boot_notification_test.send_boot_notification_required_optional_complete_payload(),
                    boot_notification_test.send_boot_notification_optional_only_payload(),
                    boot_notification_test.send_boot_notification_incomplete_required_payload(),
                    boot_notification_test.send_boot_notification_wrong_payload_data_type(),
                    boot_notification_test.send_boot_notification_no_payload(),
                    boot_notification_test.send_boot_notification_over_max_length_payload(),
                ),
                timeout=10,  # Adjust the timeout value as needed
            )
        except asyncio.TimeoutError:
            await ws.close()
            print("WebSocket connection closed.")


if __name__ == "__main__":
    try:
        asyncio.run(run_boot_notification())
    except Exception as e:
        logging.error(f"Error: {e}")
