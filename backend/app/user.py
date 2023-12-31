from typing import Any
from .chat import Chat


class UserManager:
    def __init__(self):
        self.user: dict[str, dict] = {}

    def set(self, id: str, data: dict):
        if id == "":
            return False
        if self.get(id) is None:
            self.user[id] = {}
        if data is None:
            return False
        for item in data:
            self.user[id][item] = data[item]
        return True

    def get(self, id: str):
        return self.user.get(id)

    def append(self, id: str, key: str, value: Any):
        if id == "":
            return False
        if self.get(id) is None:
            self.user[id] = {}
        if key == "":
            return False
        self.user[id][key] = value
        return True

    def remove(self, id: str, key: str):
        if id == "":
            return False
        if self.get(id) is None:
            self.user[id] = {}
        if key == "":
            del self.user[id]
            return True
        if self.user[id].get(key) is not None:
            del self.user[id][key]
        return True

    def get_all(self):
        return self.user

    def set_history(self, id: str, chats: list[Chat]):
        if id == "":
            return False
        if self.get(id) is None:
            self.user[id] = {}
        self.get(id)["history"] = chats
        return True

    def get_history(self, id: str):
        if id == "":
            return None
        if self.get(id) is None:
            return None
        if self.user[id].get("history") is None:
            return None
        return self.user[id]["history"]

    def append_history(self, id: str, chat: Chat):
        if id == "":
            return None
        if self.get(id) is None:
            self.user[id] = {}
        if self.user[id].get("history") is None:
            self.user[id]["history"] = []
        self.user[id]["history"].append(chat)

    def pop_history(self, id: str, chat: Chat):
        if id == "":
            return None
        if self.get(id) is None:
            self.user[id] = {}
        if self.user[id].get("history") is None:
            return True
        for i in range(len(self.user[id]["history"])):
            if (
                self.user[id]["history"][i] == chat
                or self.user[id]["history"][i].chat_id == chat.chat_id
            ):
                self.user[id]["history"].pop(i)
                break

    def get_all_history(self, id: str):
        if self.user.get(id) is None:
            return None

        return self.user.get(id).get("history")
