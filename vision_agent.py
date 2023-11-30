import base64
from dotenv import load_dotenv

import openai
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app import crud

def get_audio_highlight(segment):
    prompt = f"Is the following audio segment from a video a highlight? If yes, summarize it.\n\nSegment: \"{segment['text']}\""
    try:
        response = openai.Completion.create(
            engine="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=50,
            temperature=0.3
        )

        content = response.choices[0].text.strip()
        if content.lower().startswith("yes"):
            summary = content[len("yes"):].strip().lstrip(',').strip()
            return {
                'start_time': segment['start'],
                'highlight': summary
            }
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def vision_agent(
    db: Session,
    video_id: int,
    user_input: str,
    end_sec: int,
    context_len: int,
    reactor: str,
):
    # end_sec needs to be dynamically defined by identifying at which second the user started talking in the video

    # encode frames
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    # get keys
    load_dotenv()

    start_sec = max(1, end_sec - context_len)
    frames_context = crud.frame.get(
        db=db, video_id=video_id, start_sec=start_sec, end_sec=end_sec
    )
    if not frames_context:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video w/ id {video_id} has no frames from {start_sec} to {end_sec}",
        )

    for idx in range(len(frames_context)):
        file_path = frames_context[idx]
        if file_path.lower().endswith((".png", ".jpg", ".jpeg")):
            # Encode the image to base64 strings and replace
            frames_context[idx] = encode_image(file_path)

    res = crud.audiotext.get(
        db=db, video_id=video_id, start_sec=start_sec, end_sec=end_sec
    )
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Video w/ id {video_id} has no audio transcript from {start_sec} to {end_sec}",
        )

    audio_context = " ".join(res)

    PROMPT_MESSAGES = [
        {
            "role": "user",
            "content": [
                f"You are a YouTube reactor like {reactor}. Your job is to be hype. React to the video content as you watch with your friend and respond to your friend if they say something. Given are the frames of a video from second {start_sec} to {end_sec}. During this time, the video also said: '{audio_context}'. Your friend said: '{user_input}'",
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

    response = openai.audio.speech.create(model="tts-1", voice="nova", input=text)

    # Retrieve audio transcriptions
    transcript_segments = audio_context
    
    # Extract highlights from each audio segment
    audio_highlights = [get_audio_highlight(segment) for segment in transcript_segments]
    
    # Filter out None values
    audio_highlights = [highlight for highlight in audio_highlights if highlight]

    highlights_info = []
    if audio_highlights:
        # Store highlights' information in a list
        for highlight in audio_highlights:
            highlights_info.append({
                'start_time': highlight['start_time'],
                'highlight': highlight['highlight']
            })



    return response, text, highlights_info
