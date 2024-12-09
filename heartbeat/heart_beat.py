import jsonschema
from message_testing_tool.utils.logger import setup_logger
import websockets
from ocpp.v16 import ChargePoint as cp
from ocpp.v16 import call
from .schema import heartbeat_response_schema
from message_testing_tool.core.config import Config
import asyncio


logging = setup_logger(__name__)


def positive_test(response: dict, test_title: str):
    try:
        
        assert response is not None, "No response received."
        if response.current_time is not None:
            response.currentTime = response.current_time
        response_dict = {
            "currentTime": response.currentTime,
        }
        assert response.currentTime is not None, "No currentTime received."
        assert isinstance(response.currentTime, str), "currentTime is not a string"
        jsonschema.validate(instance=response_dict, schema=heartbeat_response_schema)
        logging.info(f"{test_title} test passed")
    except jsonschema.exceptions.ValidationError as e:
        logging.error(f"Heartbeat Response Schema validation error: {e}")
        logging.error(f"{test_title} test failed")
    except AssertionError as e:
        logging.error(f"Assertion error: {e}")
        logging.error(f"{test_title} test failed")
        

class HeartBeatTest(cp):
    async def heartbeat_payload(self):
        result = call.Heartbeat()
        result = await self.call(result)
        print(result)
        positive_test(result, "Heartbeat")


async def main():
    async with websockets.connect(
        Config.WEBSOCKET_URL + Config.CHARGE_POINT_ID, subprotocols=["ocpp1.6"]
    ) as ws:
        cp_id = Config.CHARGE_POINT_ID
        heart_beat_test = HeartBeatTest(cp_id, ws)

        try:
            await asyncio.wait_for(
                asyncio.gather(
                    heart_beat_test.start(),
                    heart_beat_test.heartbeat_payload(),
                ),
                timeout=5
            )
        except asyncio.TimeoutError:
            await ws.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logging.error(f"Error: {e}")