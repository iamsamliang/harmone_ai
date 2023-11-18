import os
import uuid
from typing import Annotated

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi import Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from openai.resources.audio.speech import HttpxBinaryResponseContent
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .connectionManager import ConnectionManager
from .user import UserManager
from .chat import Chat
from .database import get_db
from app import utils, agent, crud
from app.utils.text_transcript import audio_to_text

app = FastAPI()

allowed_origins = ["https://harmone.framer.website"]

app.add_middleware(
    CORSMiddleware, allow_origins=allowed_origins, allow_methods=["GET", "POST"]
)

# app.mount("/static", StaticFiles(directory="static"), name="static")

manager = ConnectionManager()
user = UserManager()

### Testing with this URL from YouTube: https://www.youtube.com/watch?v=LQb8dK4MC-E&t=2s


@app.post("/user")
async def create_user(
    db: Annotated[Session, Depends(get_db)], email: str, first_name: str, last_name: str
):
    crud.user.create(db=db, email=email, first_name=first_name, last_name=last_name)


@app.get("/user/{id}")
async def get_user(db: Annotated[Session, Depends(get_db)], id: int):
    user = crud.user.get(db=db, id=id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User w/ id {user.id} doesn't exist",
        )
    return {
        "id": user.id,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }


@app.get("/client_id")
async def get_id():
    u = uuid.uuid4()
    print(user.get(u))
    while user.get(u) is not None:
        u = uuid.uuid4()
    user.append(u, "active", True)
    res = {}
    res["code"] = 0
    res["msg"] = "success"
    res["data"] = u
    return res


@app.get("/email")
async def email(client_id: str, email: str):
    ret = user.append(client_id, "email", email)
    res = {}
    if ret:
        res["code"] = 0
        res["msg"] = "success"
        res["data"] = ret
    else:
        res["code"] = -1
        res["msg"] = "error"
        res["data"] = ret
    return res


@app.post("/url")
async def extract_url(
    db: Annotated[Session, Depends(get_db)], yt_url: str, client_id: str
):
    res = {}
    res["code"] = -1
    res["msg"] = "error"
    res["data"] = ""
    history_list = user.get_history(client_id)
    # 这是当前用户的历史消息
    print(history_list)

    try:
        utils.pipeline(db=db, yt_url=yt_url)
        db.commit()
        chat = Chat(chat_id=uuid.uuid4(), role="user", content=yt_url, is_url=True)
        user.append_history(client_id, chat)

        chat = Chat(chat_id=uuid.uuid4(), role="user", content="test", is_url=False)
        user.append_history(client_id, chat)

        res["code"] = 0
        res["msg"] = "success"
        res["data"] = ""
        return res
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.post("/sayToAI")
async def say_to_ai(
    db: Annotated[Session, Depends(get_db)],
    # file: UploadFile,
    client_id: str,
    yt_url: str,
    end_sec: int,
    context_len: int = 10,
    reactor: str = "iShowSpeed",
):
    res = {}
    res["code"] = -1
    res["msg"] = "error"
    res["data"] = ""

    # end_sec is the time in the video when the user started talking. Needs to be converted to seconds
    # round to the nearest second, using round() function
    end_sec = max(2, end_sec)

    context_len = max(1, context_len)  # defined in seconds, whole number

    chat = Chat(chat_id=uuid.uuid4(), role="user", content=yt_url, is_url=True)
    user.append_history(client_id, chat)

    # user_input = audio_to_text(file)
    user_input = "Oh my god. What is Draymond Green doing right now ?! NO ONE EVEN SCORED A POINT YET and they're fighting!"

    chat = Chat(chat_id=uuid.uuid4(), role="user", content=user_input, is_url=False)
    user.append_history(client_id, chat)

    # agent needs yt_url unless there's a better way to structure/remember this
    video = crud.video.get(db=db, yt_url=yt_url)
    if not video:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video w/ id {video.id} doesn't exist",
        )

    try:
        response, text = agent.vision_agent(
            db=db,
            video_id=video.id,
            user_input=user_input,
            end_sec=end_sec,
            context_len=context_len,
            reactor=reactor,
        )

        # await say_to_user(client_id, text, response)

        return res
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# todo 如果有反馈信息需要返回给extensions，随时随地调用say_to_user推送给extensions
# push voice to extensions
async def say_to_user(client_id: str, text: str, audio: HttpxBinaryResponseContent):
    chat = Chat(chat_id=uuid.uuid4(), role="assistant", content=text, is_url=False)
    user.append_history(client_id, chat)

    audio_file = str(uuid.uuid4()) + ".mp3"
    audio_full_path = os.path.join(os.getcwd(), os.path.join("static", audio_file))
    audio.stream_to_file(audio_full_path)
    audio.close()
    # await send_message(client_id, audio_file)


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
    except WebSocketDisconnect:
        manager.disconnect(client_id)
