import os
import uuid
import json
from io import BytesIO
from typing import Annotated

from fastapi import FastAPI, Form, UploadFile, WebSocket, WebSocketDisconnect, Response, BackgroundTasks
from fastapi import Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import openai
from openai.resources.audio.speech import HttpxBinaryResponseContent  # type: ignore
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from connection_manager import ConnectionManager
from user import UserManager
from chat import Chat
from database import get_db
from utils import pipeline
from agent import vision_agent
from schemas import UserCreateRequest
from crud import crud_video, crud_user

app = FastAPI()

allowed_origins = ["https://harmone.framer.website"]

app.add_middleware(
    CORSMiddleware, allow_origins=allowed_origins, allow_methods=["GET", "POST"]
)

if not os.path.exists("static"):
    os.makedirs("static")
if not os.path.exists("video-static"):
    os.makedirs("video-static")

app.mount("/static", StaticFiles(directory="static"), name="static")

manager = ConnectionManager()
user = UserManager()


### Testing with this URL from YouTube: https://www.youtube.com/watch?v=LQb8dK4MC-E&t=2s


@app.get("/")
async def home():
    return {"data": "", "msg": "success", "code": 0}


@app.post("/hapi/user")
async def create_user(
        db: Annotated[Session, Depends(get_db)], user_data: UserCreateRequest
):
    try:
        user = crud_user.user.create(
            db=db,
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
        )
        db.commit()
        return {"data": user.id, "msg": "success", "code": 0}
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/hapi/user/{id}")
async def get_user(db: Annotated[Session, Depends(get_db)], id: int):
    user = crud_user.user.get(db=db, id=id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User w/ id {id} doesn't exist",
        )
    return {
        "code": 0,
        "msg": "success",
        "data": {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
    }


@app.get("/hapi/client_id")
async def get_id():
    u = uuid.uuid4()
    print(user.get(str(u)))
    while user.get(str(u)) is not None:
        u = uuid.uuid4()
    user.append(str(u), "active", True)
    res = {}
    res["code"] = 0
    res["msg"] = "success"
    res["data"] = u.__str__()
    return JSONResponse(content=res, status_code=200)


@app.get("/hapi/email")
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


@app.post("/hapi/url")
async def extract_url(db: Annotated[Session, Depends(get_db)], request: Extract):
    history_list = user.get_history(request.client_id)
    # 这是当前用户的历史消息
    print(history_list)

    try:
        video = pipeline(db=db, yt_url=request.yt_url)
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
    res = {}
    res["code"] = 0
    res["msg"] = "success"
    res["data"] = video
    return res

async def say_to_ai(
        db: Session,
        file: bytes,
        client_id: str,
        yt_url: str,
        end_sec: int,
        context_len: int = 10,
        reactor: str = "iShowSpeed",
) -> tuple[HttpxBinaryResponseContent, str]:
    # end_sec is the time in the video when the user started talking. Needs to be converted to seconds
    # round to the nearest second, using round() function
    end_sec = max(2, end_sec)
    context_len = max(1, context_len)  # defined in seconds, whole number

    chat = Chat(chat_id=str(uuid.uuid4()), role="user", content=yt_url, is_url=True)
    user.append_history(client_id, chat)

    try:
        file_like = BytesIO(file)

        user_input = openai.audio.transcriptions.create(
            model="whisper-1",
            file=file_like,  # Using the file-like object directly
            language="en",
            response_format="text",
        )

        assert type(user_input) == str
        # user_input = "Oh my god. What is Draymond Green doing right now ?! NO ONE EVEN SCORED A POINT YET and they're fighting!"

        chat = Chat(
            chat_id=str(uuid.uuid4()), role="user", content=user_input, is_url=False
        )
        user.append_history(client_id, chat)

        # agent needs yt_url unless there's a better way to structure/remember this
        video = crud_video.get(db=db, yt_url=yt_url)
        if not video:
            raise Exception(f"Video w/ url {yt_url} doesn't exist")

        response, text = vision_agent(
            db=db,
            video_id=video.id,
            user_input=user_input,
            end_sec=end_sec,
            context_len=context_len,
            reactor=reactor,
        )

        assert type(text) == str
        # prepare AI output to extension
        chat = Chat(
            chat_id=str(uuid.uuid4()), role="assistant", content=text, is_url=False
        )
        user.append_history(client_id, chat)

        # audio_file = str(uuid.uuid4()) + ".mp3"
        # audio_full_path = os.path.join(os.getcwd(), os.path.join("static", audio_file))
        # response.stream_to_file(audio_full_path)
        # response.close()

        return response, text

        # return AI output to extension
        # await manager.send_personal_message(client_id, f"{audio_file}")
    except WebSocketDisconnect:
        raise WebSocketDisconnect
    except Exception:
        raise Exception


@app.websocket("/hapi/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(client_id, websocket)
    coro = manager.send_personal_message(id=client_id, message="Welcome to the chat")
    await coro
    try:
        while True:
            # Receive the JSON text message first
            print("waiting to receive data")
            text_data = await websocket.receive_text()
            timestamp_data = json.loads(text_data)
            if timestamp_data.get("action") == "test":
                coro = manager.send_personal_message(id=client_id, message=json.dumps({"action": "test", "data": "http://localhost:8089/static/356596524.mp3"}))
                await coro
                continue
            end_sec = round(timestamp_data.get("timestamp"))
            yt_url = timestamp_data.get("ytUrl")
            print(end_sec)
            print(yt_url)
            print(client_id)

            # Then, receive the binary audio data
            audio_data = await websocket.receive_bytes()
            print(type(audio_data))

            for db in get_db():
                print("processing data and returning AI output")
                response, text = await say_to_ai(
                    db=db,
                    file=audio_data,
                    client_id=client_id,
                    yt_url=yt_url,
                    end_sec=end_sec,
                )
                ai_audio = await response.aread()
                await websocket.send_bytes(ai_audio)
                await websocket.send_text(json.dumps({"type": "text", "data": text}))
                print("finished")
    except WebSocketDisconnect:
        print("disconnecting")
        manager.disconnect(client_id)
    except Exception as e:
        error_message = {"type": "error", "message": str(e)}
        await websocket.send_json(error_message)


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

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8089)
