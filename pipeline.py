import os
import json
from dotenv import load_dotenv
from download import dl_video_audio, extract_vid_info
from text_transcript import audio_to_text, format_audio
from extract_frames import extract_frames
from image_captioning import get_captions
from db_config import connect_db, add_data, exists


def pipeline(yt_url: str):
    """Extracts frames and audio of YouTube video from the given URL

    Args:
        yt_url (str): YouTube video URL
    """
    load_dotenv()
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    engine = connect_db(db_user, db_password)

    # download youtube video and audio separately
    if not exists(engine, yt_url):
        vid_file = "yt_vid"  # do not add extensions (.mp4, etc) here
        audio_file = "yt_audio"  # do not add extensions (.mp4, etc) here
        dl_video_audio(yt_url, vid_file, audio_file)
        vid_info = extract_vid_info(yt_url)

        # convert audio to text
        audio_path = audio_file + ".webm"
        transcription = audio_to_text(audio_path)
        # Save as JSON
        json_path = "vid_transcript.json"
        with open(json_path, "w") as f:
            json.dump(transcription, f, indent=4)

        # format audio as text for adding to PostgreSQL DB
        audio_texts = format_audio(json_path)

        # Store audio as text embeddings in Pinecone
        # store_transcription(json_path, openai_key, pcone_key, embedding_model, vid_info)

        # convert yt video to frames per second. Store in directory "frames"
        video_path = vid_file + ".webm"
        image_dir = "frames"
        extract_frames(video_path, image_dir)

        # convert frames to captions
        # captions = get_captions(image_dir, device)

        # Optional to save as intermediate step
        # with open("captions.json", "w") as f:
        #     json.dump(captions, f, indent=4)
        # with open("captions.json", "r") as f:
        #     captions = json.load(f)

        # store video, captions, and audio transcript in PostgreSQL DB
        add_data(engine, vid_info, captions, audio_texts)
        # store_captions(captions, vid_info, db_user, db_password) # no longer needed as we feed frames to model
