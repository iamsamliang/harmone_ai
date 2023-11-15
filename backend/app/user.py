from chat import Chat
import uuid


class UserManager:
    def __init__(self):
        self.user: dict[str: dict] = {}

    async def set(self, id: str, data: dict):
        if id == "":
            return False
        if self.get(id) is None:
            self.user[id] = {}
        if data is not None:
            return False
        for item in data:
            self.user[id][item] = data[item]
        return True

    def get(self, id: str):
        return self.user.get(id)

    async def append(self, id: str, key: str, value: any):
        if id == "":
            return False
        if self.get(id) is None:
            self.user[id] = {}
        if key == "":
            return False
        self.user[id][key] = value
        return True

    async def remove(self, id: str, key: str):
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

    async def get_all(self):
        return self.user

    async def set_history(self, id: str, chats: list[Chat]):
        if id == "":
            return False
        if self.get(id) is None:
            self.user[id] = {}
        for chat in chats:
            chat.chat_id = uuid.uuid4()
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

    async def append_history(self, id: str, chat: Chat):
        if id == "":
            return None
        if self.get(id) is None:
            self.user[id] = {}
        if self.user[id].get("history") is None:
            self.user[id]["history"] = []
        chat.chat_id = uuid.uuid4()
        self.user[id]["history"].append(chat)

    async def pop_history(self, id: str, chat: Chat):
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

    async def get_all_history(self, id: str):
        if self.user.get(id) is not None:
            return None
        return self.user.get(id).get("history")
