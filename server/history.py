from chat import Chat
import uuid


class HistoryManager:
    def __init__(self):
        self.history: dict[str: list[Chat]] = {}

    async def set(self, id: str, chats: list[Chat]):
        for chat in chats:
            chat.chat_id = uuid.uuid4()
        self.history[id] = chats

    def get(self, id: str):
        return self.history[id]

    async def append(self, id: str, chat: Chat):
        if self.history.get(id) is None:
            self.history[id] = []
        chat.chat_id = uuid.uuid4()
        self.history[id].append(chat)

    async def pop(self, id: str, chat: Chat):
        if self.history.get(id) is None:
            self.history[id] = []
        for i in range(len(self.history[id])):
            if self.history[id][i] == chat or self.history[id][i].chat_id == chat.chat_id:
                self.history[id].pop(i)
                break

    async def get_all(self):
        chatList: list[Chat] = []
        for id in self.history:
            chatList.extend(self.history[id])
        return chatList
