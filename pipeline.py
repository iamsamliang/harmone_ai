import os
import json
from dotenv import load_dotenv
from download import dl_video_audio, extract_vid_info
from text_transcript import audio_to_text, store_transcription, format_json
from extract_frames import extract_frames
from image_captioning import get_captions
from db_config import connect_db, add_data

device = "mps"  # Apple GPU
load_dotenv()

# download youtube video and audio separately
yt_url = "https://www.youtube.com/watch?v=hn0cygb3GLo"
# output_file = "test_yt"  # do not add extensions (.mp4, etc) here
# dl_video_audio(yt_url, output_file)
vid_info = extract_vid_info(yt_url)

# convert audio to text
# audio_file = output_file + "_audio.webm"
json_path = "transcription.json"
# transcription = audio_to_text(audio_file, device_n=device)
# # Save as JSON
# with open(json_path, "w") as f:
#     json.dump(transcription, f, indent=4)

# format audio as text for adding to PostgreSQL DB
audio_texts = format_json(json_path)

# Store text embeddings in Pinecone
# store_transcription(json_path, openai_key, pcone_key, embedding_model, vid_info)

# convert yt video to frames per second. Store in directory "frames"
# video_path = output_file + ".webm"
# image_dir = "frames"
# extract_frames(video_path, image_dir)

# convert frames to captions
# captions = get_captions(image_dir, device)

# Optional to save as intermediate step
# with open("captions.json", "w") as f:
#     json.dump(captions, f, indent=4)
with open("captions.json", "r") as f:
    captions = json.load(f)

# store video, captions, and audio transcript in PostgreSQL DB
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
engine = connect_db(db_user, db_password)
add_data(engine, vid_info, captions, audio_texts)
# store_captions(captions, vid_info, db_user, db_password)
