class UserManager:
    def __init__(self):
        self.user: dict[str: dict] = {}

    async def set(self, id: str, data: dict):
        if id == "":
            return False
        if self.user.get(id) is None:
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
        if self.user.get(id) is None:
            self.user[id] = {}
        if key == "":
            return False
        self.user[id][key] = value
        return True

    async def remove(self, id: str, key: str):
        if id == "":
            return False
        if self.user.get(id) is None:
            self.user[id] = {}
        if key == "":
            del self.user[id]
            return True
        if self.user[id].get(key) is not None:
            del self.user[id][key]
        return True

    async def get_all(self):
        return self.user
