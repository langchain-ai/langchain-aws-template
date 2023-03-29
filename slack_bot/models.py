from typing import Dict


class SlackMessage:
    """Encapsulates the message sent by slack api"""

    def __init__(self, body: Dict):
        self.body = body
        self.message_event = body["event"]
        self.event_id = body["event_id"] 
        self.channel = self.message_event["channel"]
        self.text = self.message_event["text"]
        if "authorizations" in body:
            self.authorizations = body["authorizations"]
        else:
            self.authorizations = []
        
        if "thread_ts" in self.message_event:
            self.thread = self.message_event["thread_ts"]
        else:
            self.thread = self.message_event["ts"]

    def is_bot_reply(self):
        return "bot_id" in self.message_event

    def get_bot_id(self):
        if not self.authorizations:
            return ""

        return self.authorizations[0]["user_id"]

    def is_direct_message(self):
        bot_id = self.get_bot_id()
        return bot_id and f"<@{bot_id}>" in self.text

    def sanitized_text(self):
        """Removes bot id from direct messages"""

        bot_id = self.get_bot_id()
        if not bot_id:
            return self.text
        return self.text.replace(f"<@{bot_id}>", "").strip()
