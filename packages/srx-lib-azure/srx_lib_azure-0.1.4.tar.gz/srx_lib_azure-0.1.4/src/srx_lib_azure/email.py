import os
from azure.communication.email.aio import EmailClient

import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Thin wrapper over Azure Communication Services EmailClient."""

    def __init__(self):
        self.connection_string = os.getenv("ACS_CONNECTION_STRING")
        self.sender_address = os.getenv("EMAIL_SENDER")
        if not self.connection_string or not self.sender_address:
            raise ValueError("Missing ACS_CONNECTION_STRING or EMAIL_SENDER in environment variables")
        self.email_client = EmailClient.from_connection_string(self.connection_string)

    async def send_notification(self, recipient: str, subject: str, body: str, html: bool = False):
        message = {
            "content": {"subject": subject},
            "recipients": {"to": [{"address": recipient}]},
            "senderAddress": self.sender_address,
        }
        if html:
            message["content"]["html"] = body
        else:
            message["content"]["plainText"] = body
        try:
            poller = await self.email_client.begin_send(message)
            result = await poller.result()
            message_id = result.get("id")
            if message_id:
                logger.info("Email sent to %s with Message ID: %s", recipient, message_id)
                return {"status": "success", "message": "Email sent successfully", "message_id": message_id}
            logger.error("Failed to send email. Result: %s", result)
            return {"status": "error", "message": f"Failed to send email: {result}"}
        except Exception as e:
            logger.error("Email send exception: %s", e)
            return {"status": "error", "message": str(e)}

