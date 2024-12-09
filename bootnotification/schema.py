# Define the JSON schema for the BootNotification response
boot_notification_response_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "BootNotificationResponse",
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "additionalProperties": False,
            "enum": ["Accepted", "Pending", "Rejected"],
        },
        "currentTime": {"type": "string", "format": "date-time"},
        "interval": {"type": "integer"},
    },
    "additionalProperties": False,
    "required": ["status", "currentTime", "interval"],
}
