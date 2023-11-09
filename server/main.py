from fastapi import FastAPI, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from connectionManager import ConnectionManager
from history import HistoryManager
import uuid
from pipeline import pipeline
from text_transcript import audio_to_text
from agent import companion

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
    yt_url = "https://www.youtube.com/watch?v=hn0cygb3GLo"  # remove later
    pipeline(yt_url)

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

    # end_sec is the time in the video when the user started talking. Needs to be converted to seconds
    # round to the nearest second, using round() function
    end_sec = max(2, 238)  # remove later. This needs to be passed into this function
    context_len = 10  # defined in seconds, whole number. This is a parameter to be passed into this func
    reactor = "iShowSpeed"  # param
    # todo 解析voice to text

    user_input = audio_to_text(file)

    # todo 上一步调用完成后，需要把解析好的文字数据存储到history

    # todo 此处需要sam补充function调用
    yt_url = "https://www.youtube.com/watch?v=hn0cygb3GLo"  # remove later
    # agent needs yt_url unless there's a better way to structure/remember this
    text_resp, audio_resp = companion(user_input, yt_url, end_sec, context_len, reactor)

    # NOTE: audio_resp is the Audio object returned from openai.

    say_to_user(client_id, audio_resp)
    send_message(client_id, text_resp)

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
