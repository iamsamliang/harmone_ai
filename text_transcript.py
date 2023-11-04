import whisper
import json
import pinecone
import cohere
from uuid import uuid4


def audio_to_text(audio_file, device_n):
    # old way to extract audio
    # command = f"ffmpeg -i {video_file} -q:a 0 {output_file}"
    # subprocess.run(command, shell=True, check=True)

    # english only model for speed
    model = whisper.load_model("base.en", device=device_n)
    result = model.transcribe(audio_file)  # mp3 or webm

    return result


def store_transcription(json_path, cohere_key, pcone_key, model_name, vid_info):
    # load the Pinecone Index
    pinecone.init(api_key=pcone_key, environment="gcp-starter")
    index = pinecone.Index("ai-companion")

    # load JSON object
    with open(json_path, "r") as json_file:
        json_object = json.load(json_file)

    # setup the name of the model we want to use, the API key, and the input type.
    input_type_embed = "search_document"

    co = cohere.Client(cohere_key)

    texts = []
    segments = json_object["segments"]
    for segment in segments:
        # relevant segment keys = { "start", "end", "text" }
        # "start": 0.0, "end": 7.0, "text": " Hardaway 19, Kyrie 17, power 11, O'Neill with a three."

        template = f'From second {segment["start"]} to second {segment["end"]}, the video said {segment["text"]}'
        texts.append(template)

    # get the embeddings
    embeds = co.embed(
        texts=texts, model=model_name, input_type=input_type_embed
    ).embeddings

    start_idx = 0
    batch_limit = 100
    embed_len = len(embeds)
    # need metadata to do filtered search
    metadata = [{"url": vid_info["url"]}] * batch_limit

    # add embeddings to index
    while start_idx < embed_len:
        ids = [str(uuid4()) for _ in range(batch_limit)]
        end_idx = min(start_idx + batch_limit, embed_len)
        index.upsert(vectors=zip(ids, embeds[start_idx:end_idx], metadata))
        start_idx = end_idx
