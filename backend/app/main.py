import os
import uuid
from typing import Annotated

from fastapi import FastAPI, Form, UploadFile, WebSocket, WebSocketDisconnect
from fastapi import Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import openai
from openai.resources.audio.speech import HttpxBinaryResponseContent
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .connectionManager import ConnectionManager
from .user import UserManager
from .chat import Chat
from .database import get_db
from app import utils, agent, crud, schemas
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


@app.get("/")
async def home():
    return {"data": "success"}


@app.post("/user")
async def create_user(
    db: Annotated[Session, Depends(get_db)], user_data: schemas.UserCreateRequest
):
    try:
        crud.user.create(
            db=db,
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
        )
        db.commit()
        return {"data": "success"}
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/user/{id}")
async def get_user(db: Annotated[Session, Depends(get_db)], id: int):
    user = crud.user.get(db=db, id=id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User w/ id {id} doesn't exist",
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
    print(user.get(str(u)))
    while user.get(str(u)) is not None:
        u = uuid.uuid4()
    user.append(str(u), "active", True)
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


class Extract(BaseModel):
    yt_url: str
    client_id: str


@app.post("/url", status_code=status.HTTP_204_NO_CONTENT)
async def extract_url(db: Annotated[Session, Depends(get_db)], request: Extract):
    history_list = user.get_history(request.client_id)
    # 这是当前用户的历史消息
    print(history_list)

    try:
        utils.pipeline(db=db, yt_url=request.yt_url)
        db.commit()
        chat = Chat(
            chat_id=str(uuid.uuid4()), role="user", content=request.yt_url, is_url=True
        )
        user.append_history(request.client_id, chat)

        chat = Chat(
            chat_id=str(uuid.uuid4()), role="user", content="test", is_url=False
        )
        user.append_history(request.client_id, chat)
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


class UserInput(BaseModel):
    

@app.post("/sayToAI")
async def say_to_ai(
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile,
    client_id: Annotated[str, Form()],
    yt_url: Annotated[str, Form()],
    end_sec: Annotated[int, Form()],
    context_len: Annotated[int, Form(10)],
    reactor: Annotated[str, Form("iShowSpeed")]
):
    res = {}
    res["code"] = -1
    res["msg"] = "error"
    res["data"] = ""

    # end_sec is the time in the video when the user started talking. Needs to be converted to seconds
    # round to the nearest second, using round() function
    end_sec = max(2, end_sec)

    context_len = max(1, context_len)  # defined in seconds, whole number

    chat = Chat(chat_id=str(uuid.uuid4()), role="user", content=yt_url, is_url=True)
    user.append_history(client_id, chat)
    
    try:
        # Rewind the file to the beginning if it has been read before
        await file.seek(0)

        user_input = openai.audio.transcriptions.create(
            model="whisper-1", 
            file=file.file,  # Using the file-like object directly
            language="en",
            response_format="text"
        )
        
        assert type(user_input) == str
        # user_input = "Oh my god. What is Draymond Green doing right now ?! NO ONE EVEN SCORED A POINT YET and they're fighting!"

        chat = Chat(
            chat_id=str(uuid.uuid4()), role="user", content=user_input, is_url=False
        )
        user.append_history(client_id, chat)

        # agent needs yt_url unless there's a better way to structure/remember this
        video = crud.video.get(db=db, yt_url=yt_url)
        if not video:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Video w/ url {yt_url} doesn't exist",
            )

        response, text = agent.vision_agent(
            db=db,
            video_id=video.id,
            user_input=user_input,
            end_sec=end_sec,
            context_len=context_len,
            reactor=reactor,
        )

        # prepare AI output to extension
        chat = Chat(chat_id=str(uuid.uuid4()), role="assistant", content=text, is_url=False)
        user.append_history(client_id, chat)

        audio_file = str(uuid.uuid4()) + ".mp3"
        audio_full_path = os.path.join(os.getcwd(), os.path.join("static", audio_file))
        response.stream_to_file(audio_full_path)
        response.close()
        
        # return AI output to extension
        await manager.send_personal_message(client_id, f"{audio_file}")
    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
        


# todo 如果有反馈信息需要返回给extensions，随时随地调用say_to_user推送给extensions
# push voice to extensions
# async def say_to_user(client_id: str, text: str, audio: HttpxBinaryResponseContent):
#     chat = Chat(chat_id=str(uuid.uuid4()), role="assistant", content=text, is_url=False)
#     user.append_history(client_id, chat)

#     audio_file = str(uuid.uuid4()) + ".mp3"
#     audio_full_path = os.path.join(os.getcwd(), os.path.join("static", audio_file))
#     audio.stream_to_file(audio_full_path)
#     audio.close()
#     await send_message(client_id, audio_file)


# push message to extensions
# async def send_message(client_id: str, data: str):
#     try:
#         await manager.send_personal_message(client_id, f"{data}")
#     except WebSocketDisconnect:
#         manager.disconnect(client_id)
#         return False
#     return True


@app.websocket("/api/ws")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(client_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(client_id)
