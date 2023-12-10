import os.path
import sys
import uuid

from urllib.parse import urlparse, parse_qs
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .download import dl_video_audio, extract_vid_info

sys.path.append('..')
from app import crud_video, crud_frame, crud_audio as crud_audiotext

    # download youtube video and audio separately

def pipeline(db: Session, yt_url: str):
    if not yt_url:
        return None
    pUrl = urlparse(yt_url)
    params = parse_qs(pUrl.query)
    if "v" not in params or params["v"] is None or len(params["v"]) == 0:
        return None
    videoId = params["v"][0]
    video = crud_video.video.get(db=db, yt_url=yt_url)
    if not video:
        vid_file = os.path.join("video-static", f"{videoId}_vid")  # do not add extensions (.mp4, etc) here
        audio_file = os.path.join("video-static", f"{videoId}_audio")  # do not add extensions (.mp4, etc) here
        dl_video_audio(yt_url, vid_file, audio_file)
        vid_info = extract_vid_info(yt_url)

        try:
            created_vid_obj = crud_video.video.create(db=db, video=vid_info)
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        # convert audio to text
        audio_path = audio_file + ".webm"
        transcription = audio_to_text(audio_path).model_dump()
        # Save as JSON
        # json_path = "vid_transcript.json"
        # with open(json_path, "w") as f:
        #     json.dump(transcription, f, indent=4)

        # format audio as text for adding to PostgreSQL DB
        audio_texts = format_audio(transcription)
        try:
            crud_audiotext.audiotext.create(
                db=db, video_id=created_vid_obj.id, audio_texts=audio_texts
            )
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        # Store audio as text embeddings in Pinecone
        # store_transcription(json_path, openai_key, pcone_key, embedding_model, vid_info)

        # convert yt video to frames per second. Store in directory "frames"
        video_path = vid_file + ".mp4"
        output_dir = os.path.join("video-static", f"frames/{str(videoId)}")
        try:
            ok = extract_frames(video_path, output_dir)
            if not ok:
                return False
            crud_frame.frame.create(db=db, vid_id=created_vid_obj.id, output_dir=output_dir)
        except IntegrityError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except FileExistsError as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        # convert frames to captions
        # captions = get_captions(image_dir, device)

        # Optional to save as intermediate step
        # with open("captions.json", "w") as f:
        #     json.dump(captions, f, indent=4)
        # with open("captions.json", "r") as f:
        #     captions = json.load(f)

        # store video, captions, and audio transcript in PostgreSQL DB
        # add_data(engine, vid_info, captions, audio_texts)
        # store_captions(captions, vid_info, db_user, db_password) # no longer needed as we feed frames to model
        return created_vid_obj

    return video
