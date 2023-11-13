import base64
import os
from dotenv import load_dotenv
from db_config import connect_db, db_get_transcript
import openai


def vision_companion(user_input, yt_url, end_sec, context_len, reactor):
    # encode frames
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    # get keys
    load_dotenv()
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")

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

    # end_sec needs to be dynamically defined by identifying at which second the user started talking in the video
    start_sec = max(1, end_sec - context_len)
    frames_context = base64_images[start_sec : end_sec + 1]

    engine = connect_db(db_user, db_password)
    res = db_get_transcript(engine, yt_url, start_sec, end_sec)
    audio_context = " ".join(res)

    PROMPT_MESSAGES = [
        {
            "role": "user",
            "content": [
                f"You are a YouTube reactor like {reactor}. Your job is to be hype. React to the video content as you watch with your friend and respond to your friend if they say something. Given are the frames of a video from second {start_sec} to {end_sec}. During this time, the video said: '{audio_context}'. Your friend said: '{user_input}'",
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
    text = result.choices[0].message.content

    response = openai.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text,
    )

    return response


yt_url = "https://www.youtube.com/watch?v=hn0cygb3GLo"
user_input = "nothing"
reactor = "IShowSpeed"
context_len = 2  # defined in seconds
end_sec = max(2, 238)
