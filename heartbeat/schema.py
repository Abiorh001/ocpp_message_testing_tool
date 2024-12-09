heartbeat_response_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "HeartbeatResponse",
    "type": "object",
    "properties": {
        "currentTime": {
            "type": "string",
            "format": "date-time"
        }
    },
    "additionalProperties": False,
    "required": [
        "currentTime"
    ]
}