import os
import json
from dotenv import load_dotenv
from download import dl_video_audio
from text_transcript import audio_to_text, store_transcription
from extract_frames import extract_frames
from image_captioning import get_captions, store_captions

device = "mps"  # Apple GPU

# download youtube video and audio separately
yt_url = "https://www.youtube.com/watch?v=hn0cygb3GLo"
output_file = "test_yt"  # do not add extensions (.mp4, etc) here
vid_info = dl_video_audio(yt_url, output_file)

# convert audio to text
audio_file = output_file + "_audio.webm"
json_path = "transcription.json"
transcription = audio_to_text(audio_file, device_n=device)
# Save as JSON
with open(json_path, "w") as f:
    json.dump(transcription, f, indent=4)

# Store text embeddings in Pinecone
load_dotenv()
cohere_key = os.getenv("COHERE_API_KEY")
pcone_key = os.getenv("PINECONE_API_KEY")
model = "embed-english-v3.0"
store_transcription(json_path, cohere_key, pcone_key, model)

# convert yt video to frames per second. Store in directory "frames"
video_path = output_file + ".webm"
image_dir = "frames"
extract_frames(video_path, image_dir)

# convert frames to captions
captions = get_captions(image_dir, device)

# Optional to save as intermediate step
# with open("captions.json", "w") as f:
#     json.dump(captions, f, indent=4)
# with open("captions.json", "r") as f:
#     captions = json.load(f)

# store in database along with video information
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
store_captions(captions, vid_info, db_user, db_password)
