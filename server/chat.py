class Chat:
    def __init__(self, chat_id: str, role: str, content: str, is_url: bool):
        self.chat_id = chat_id
        self.role = role
        self.content = content
        self.is_url = is_url
