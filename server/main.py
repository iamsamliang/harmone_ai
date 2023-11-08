from fastapi import FastAPI, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from connectionManager import ConnectionManager
from history import HistoryManager
import uuid

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

manager = ConnectionManager()
history = HistoryManager()
uuidDict = {}

@app.get("/api/generator/client_id")
async def extract_url():
    u = uuid.uuid4()
    print(uuidDict.get(u))
    while uuidDict.get(u) is not None:
        u = uuid.uuid4()
    uuidDict[u] = True
    res = {}
    res["code"] = 0
    res["msg"] = "success"
    res["data"] = u
    return res


@app.post("/api/youtube/url")
async def extract_url(url: str, client_id: str):
    res = {}
    res["code"] = -1
    res["msg"] = "服务异常"
    res["data"] = ""
    history_list = history.get(client_id)
    # 这是当前用户的历史消息
    print(history_list)

    # todo 此处需要sam补充function调用

    # todo 上一步调用完成后，需要把解析好的文字数据存储到history

    # todo 上一步调用完成后，需要把反馈的文字数据存储到history
    # todo 如果有反馈信息可以直接返回给extensions，也可以异步用websocket推送给extensions
    return res


@app.post("/api/youtube/sayToAI")
async def say_to_ai(file: UploadFile, client_id: str):
    res = {}
    res["code"] = -1
    res["msg"] = "服务异常"
    res["data"] = ""

    # todo 解析voice to text

    # todo 上一步调用完成后，需要把解析好的文字数据存储到history

    # todo 此处需要sam补充function调用

    # todo 上一步调用完成后，需要把反馈的文字数据存储到history

    # todo 如果有反馈信息可以直接返回给extensions，也可以异步用websocket推送给extensions
    return res


# push voice to extensions
async def say_to_user(client_id: str, data: str):
    # todo 需要把解析好的文字数据存储到history

    # todo 通过text合成语音

    # todo 异步用websocket推送给extensions
    await send_message(client_id, data)


# push message to extensions
async def send_message(client_id: str, data: str):
    try:
        await manager.send_personal_message(client_id, f"{data}")
    except WebSocketDisconnect:
        manager.disconnect(client_id)
        return False
    return True


@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(client_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(data)
    except WebSocketDisconnect:
        manager.disconnect(client_id)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8087)
