import whisper
import json
import pinecone
import openai
from uuid import uuid4


def audio_to_text(audio_file, device_n):
    # old way to extract audio
    # command = f"ffmpeg -i {video_file} -q:a 0 {output_file}"
    # subprocess.run(command, shell=True, check=True)

    # english only model for speed
    model = whisper.load_model("base.en", device=device_n)
    result = model.transcribe(audio_file)  # mp3 or webm

    return result


def format_json(json_path):
    # load JSON object
    with open(json_path, "r") as json_file:
        json_object = json.load(json_file)

    output = []
    segments = json_object["segments"]
    for segment in segments:
        # (start_time, end_time, text)
        output.append(
            (int(segment["start"]) + 1, int(segment["end"]) + 1, segment["text"])
        )
    return output


def store_transcription(json_path, openai_key, pcone_key, embedding_model, vid_info):
    # openai key
    openai.api_key = openai_key
    # load the Pinecone Index
    pinecone.init(api_key=pcone_key, environment="gcp-starter")
    index = pinecone.Index("ai-companion")

    # load JSON object
    with open(json_path, "r") as json_file:
        json_object = json.load(json_file)

    texts = []
    metadata = []
    segments = json_object["segments"]
    for segment in segments:
        # relevant segment keys = { "start", "end", "text" }
        # "start": 0.0, "end": 7.0, "text": " Hardaway 19, Kyrie 17, power 11, O'Neill with a three."

        # text = f'From second {int(segment["start"]) + 1} to second {int(segment["end"]) + 1}, the video said "{segment["text"]}"'
        text = f'{int(segment["start"]) + 1} to {int(segment["end"]) + 1}'
        texts.append(text)
        meta = (
            f'{int(segment["start"]) + 1}-{int(segment["end"]) + 1}: {segment["text"]}'
        )
        metadata.append({"text": meta, "url": vid_info["url"]})

    # get the embeddings
    res = openai.Embedding.create(input=texts, model=embedding_model)
    embeds = [record["embedding"] for record in res["data"]]

    start_idx = 0
    batch_limit = 100
    embed_len = len(embeds)
    # need metadata to do filtered search and retain the original text
    # metadata = [{"url": vid_info["url"]}] * batch_limit
    # metadata = [{"text": text, "url": vid_info["url"]} for text in texts]
    assert len(metadata) == embed_len

    # add embeddings to index
    while start_idx < embed_len:
        ids = [str(uuid4()) for _ in range(batch_limit)]
        end_idx = min(start_idx + batch_limit, embed_len)
        index.upsert(
            vectors=zip(ids, embeds[start_idx:end_idx], metadata[start_idx:end_idx])
        )
        start_idx = end_idx
