from fastapi import FastAPI, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from connectionManager import ConnectionManager
from history import HistoryManager
from chat import Chat
import uuid
from pipeline import pipeline
from text_transcript import audio_to_text
from agent import companion
from openai.resources.audio.speech import HttpxBinaryResponseContent
import os

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
async def extract_url(yt_url: str, client_id: str):
    res = {}
    res["code"] = -1
    res["msg"] = "error"
    res["data"] = ""
    history_list = history.get(client_id)
    # 这是当前用户的历史消息
    print(history_list)

    # todo 此处需要sam补充function调用
    # yt_url = "https://www.youtube.com/watch?v=hn0cygb3GLo"  # remove later
    parsed_text = pipeline(yt_url)

    chat = Chat()
    chat.role = "user"
    chat.content = yt_url
    chat.is_url = True
    history.append(client_id, chat)

    chat = Chat()
    chat.role = "user"
    chat.content = parsed_text
    chat.is_url = False
    history.append(client_id, chat)

    res["code"] = 0
    res["msg"] = "success"
    res["data"] = ""
    return res


@app.post("/api/youtube/sayToAI")
async def say_to_ai(file: UploadFile, client_id: str, yt_url: str, end_sec: int, context_len: int, reactor: str):
    res = {}
    res["code"] = -1
    res["msg"] = "error"
    res["data"] = ""

    if end_sec < 2 or end_sec > 238:
        end_sec = max(2, 238)  # remove later. This needs to be passed into this function

    # end_sec is the time in the video when the user started talking. Needs to be converted to seconds
    # round to the nearest second, using round() function
    if context_len < 10:
        context_len = 10  # defined in seconds, whole number. This is a parameter to be passed into this func
    if reactor == "":
        reactor = "iShowSpeed"  # param

    chat = Chat()
    chat.role = "user"
    chat.content = yt_url
    chat.is_url = True
    history.append(client_id, chat)

    user_input = audio_to_text(file)

    chat = Chat()
    chat.role = "user"
    chat.content = user_input
    chat.is_url = False
    history.append(client_id, chat)

    # yt_url = "https://www.youtube.com/watch?v=hn0cygb3GLo"  # remove later
    # agent needs yt_url unless there's a better way to structure/remember this
    text_resp, audio_resp = companion(user_input, yt_url, end_sec, context_len, reactor)
    # NOTE: audio_resp is the Audio object returned from openai.

    say_to_user(client_id, text_resp, audio_resp)

    return res

# todo 如果有反馈信息需要返回给extensions，随时随地调用say_to_user推送给extensions
# push voice to extensions
async def say_to_user(client_id: str, text: str, audio: HttpxBinaryResponseContent):
    chat = Chat()
    chat.role = "assistant"
    chat.content = text
    chat.is_url = False
    history.set(client_id, chat)

    audio_file = str(uuid.uuid4()) + ".mp3"
    audio_full_path = os.path.join(os.getcwd(), os.path.join("static", audio_file))
    audio.stream_to_file(audio_full_path)
    audio.close()
    # todo "http://127.0.0.1:8087/" later replace
    await send_message(client_id, "http://127.0.0.1:8087/static/" + audio_file)


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
