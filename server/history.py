from chat import Chat


class HistoryManager:
    def __init__(self):
        self.history: dict[str: list[Chat]] = {}

    async def set(self, id: str, chat: Chat):
        if self.history.get(id) is None:
            self.history[id] = []
        self.history[id].append(chat)

    def get(self, id: str):
        return self.history[id]

    async def get_all(self):
        chatList = []
        for id in self.history:
            chatList.extend(self.history[id])
        return chatList
