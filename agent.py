import os
from operator import itemgetter
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chat_models import ChatOpenAI
from langchain.schema.output_parser import StrOutputParser
from db_config import db_get_captions, connect_db, db_get_transcript
import openai


# Build a prompt template from the stored data, have conversational memory for LLM to react and respond to user and video
def companion(user_input, yt_url, end_sec, context_len, reactor):
    # get keys
    load_dotenv()
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    engine = connect_db(db_user, db_password)

    # load the Pinecone Index and create vectorstore as langchain component
    # pinecone.init(api_key=pcone_key, environment="gcp-starter")
    # index = pinecone.Index("ai-companion")
    # vectorstore = Pinecone(index=index, embedding=embeddings, text_key="text")

    # end_sec needs to be dynamically defined by identifying at which second the user started talking in the video
    start_sec = max(1, end_sec - context_len)

    # audio_query = f"From second {start_sec} to second {end_sec}, what did the video say?"

    # get the embedding of the query
    # embedding_model = "text-embedding-ada-002"
    # embed_query = openai.Embedding.create(input=audio_query, model=embedding_model)["data"][
    #     0
    # ]["embedding"]
    # # query the Pinecone index with the embedded query to return top 3 most relevant audio transcriptions
    # # filter by the YT URL
    # audio_context = index.query(
    #     [embed_query], top_k=6, filter={"url": {"$eq": yt_url}}, include_metadata=True
    # )

    # wrapper around vector store
    # retriever = vectorstore.as_retriever()

    # load LLM
    chat_gpt = ChatOpenAI()

    # grab audio context
    # audio_template = """Answer the question based only on the following context:
    # {context}

    # Question: {question}
    # """

    # audio_prompt = ChatPromptTemplate.from_template(audio_template)
    # chain1 = (
    #     {"context": retriever, "question": RunnablePassthrough()}
    #     | audio_prompt
    #     | chat_gpt
    #     | StrOutputParser
    # )  # need to grab by url filter

    # audio_context = chain1.invoke(audio_query)  # type string
    res = db_get_transcript(engine, yt_url, start_sec, end_sec)
    audio_context = " ".join(res)

    # Grab the image captions context; captions will be in order by time
    captions = db_get_captions(engine, yt_url, start_sec, end_sec)

    caption_template = """You're given a list of image captions that describe what happens in a video in sequential order. Your job is to summarize what happened. Retain key events and eliminate redundant information, but be as descriptive as possible.

    Image captions: {captions}
    """

    caption_prompt = ChatPromptTemplate.from_template(caption_template)

    # summary chain
    summary_chain = caption_prompt | chat_gpt | StrOutputParser()
    captions_context = summary_chain.invoke({"captions": captions})

    # create prompt template
    chat_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a YouTube reactor like {reactor} and watch videos with your friend. Your job is to crazily react to the video content as you watch with your friend and respond to your friend if they say something. You must also be accurate to what's happening in the video.",
            ),
            (
                "system",
                "From second {start_sec} to second {end_sec}, the video said: '{audio_context}', and what happened in the video is: '{captions_context}'",
            ),
            MessagesPlaceholder(variable_name="history"),
            ("human", "Your friend just said this: {user_input}"),
        ]
    )
    memory = ConversationBufferMemory(human_prefix="Friend", return_messages=True)

    # conversation chain
    chat_chain = (
        RunnablePassthrough.assign(
            history=(
                RunnableLambda(memory.load_memory_variables) | itemgetter("history")
            ),
        )
        | chat_prompt
        | chat_gpt
    )

    inputs = {
        "reactor": reactor,
        "start_sec": start_sec,
        "end_sec": end_sec,
        "audio_context": audio_context,
        "captions_context": captions_context,
        "user_input": user_input,
    }
    response = chat_chain.invoke(inputs)

    # update conversation memory
    memory.save_context(
        {"user_input": inputs["user_input"]}, {"output": response.content}
    )

    # text to speach
    # speech_file_path = Path(__file__).parent / "speech.mp3"
    audio_resp = openai.audio.speech.create(
        model="tts-1", voice="echo", input=response.content, response_format="mp3"
    )

    return response.content, audio_resp
    # response.stream_to_file(speech_file_path)
