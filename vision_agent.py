import base64
import os
from dotenv import load_dotenv
from db_config import connect_db, db_get_transcript
import openai


# encode frames
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# get keys
load_dotenv()
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

yt_url = "https://www.youtube.com/watch?v=hn0cygb3GLo"

# Path to your directory of images
directory = "frames"
# Initialize a list to hold base64 strings
base64_images = []
# Iterate over each file in the directory
for filename in sorted(os.listdir(directory)):
    if filename.lower().endswith((".png", ".jpg", ".jpeg")):
        file_path = os.path.join(directory, filename)
        # Encode the image and add the base64 string to the list
        base64_images.append(encode_image(file_path))

# curr_sec needs to be dynamically defined by identifying at which second the user started talking in the video
context_len = 2  # defined in seconds
curr_sec = max(2, 238)
start_sec = max(1, curr_sec - context_len)
frames_context = base64_images[start_sec : curr_sec + 1]

engine = connect_db(db_user, db_password)
res = db_get_transcript(engine, yt_url, start_sec, curr_sec)
audio_context = " ".join(res)

PROMPT_MESSAGES = [
    {
        "role": "user",
        "content": [
            "You are a YouTube reactor like {reactor} and watch videos with your friend. Your job is to crazily react to the video content as you watch with your friend and respond to your friend if they say something. You must also be accurate to what's happening in the video. These are the frames of a video from second {start_sec} to {curr_sec}. During this time, the video said: '{audio_context}'",
            *map(lambda x: {"image": x, "resize": 768}, frames_context),
        ],
    },
]
params = {
    "model": "gpt-4-vision-preview",
    "messages": PROMPT_MESSAGES,
    "max_tokens": 200,
}

result = openai.chat.completions.create(**params)
print(result.choices[0].message.content)
