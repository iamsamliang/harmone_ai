import pinecone
import os
import openai
from operator import itemgetter
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chat_models import ChatOpenAI
from db_config import db_get_captions, connect_db


# Build a prompt template from the stored data, have conversational memory for LLM to react and respond to user and video

# get keys
load_dotenv()
pcone_key = os.getenv("PINECONE_API_KEY")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
openai.api_key = os.getenv("OPEN_AI_KEY")

# load the Pinecone Index
pinecone.init(api_key=pcone_key, environment="gcp-starter")
index = pinecone.Index("ai-companion")

# create vectorstore as langchain component
# vectorstore = Pinecone(index=index, embedding=embeddings, text_key="text")

yt_url = "https://www.youtube.com/watch?v=hn0cygb3GLo"

# curr_sec needs to be dynamically defined by identifying at which second the user
# started talking in the video
curr_sec = 238
start_sec = max(1, curr_sec - 5)
audio_query = f"From second {start_sec} to second {curr_sec}, what did the video say?"
# input_type_embed = "search_document"

### NOTE: This will be changed. This doesn't fetch the appropriate audio corresponding to the desired times ###

# get the embedding of the query
embedding_model = "text-embedding-ada-002"
embed_query = openai.Embedding.create(input=audio_query, model=embedding_model)["data"][
    0
]["embedding"]
# query the Pinecone index with the embedded query to return top 3 most relevant audio transcriptions
# filter by the YT URL
audio_context = index.query(
    [embed_query], top_k=6, filter={"url": {"$eq": yt_url}}, include_metadata=True
)
print(f"audio_context: {audio_context}\n")

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

# Grab the image captions context (previous 5 seconds)
engine = connect_db(db_user, db_password)
# list of captions in order
captions = db_get_captions(engine, yt_url, start_sec, curr_sec)

caption_template = """You're given a list of image captions that describe what happens in a video in sequential order. Your job is to summarize what happened, retaining key events and eliminating redundant information.

Image captions: {captions}
"""
caption_prompt = ChatPromptTemplate.from_template(caption_template)
# summary chain
summary_chain = caption_prompt | chat_gpt
captions_context = summary_chain.invoke({"captions": captions})
print(f"captions_context: {captions_context}\n")

# create prompt template
chat_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a YouTube reactor like {reactor} and watch videos with your friend. Your job is to crazily react to the video content as you watch with your friend and respond to your friend if they say something.",
        ),
        (
            "system",
            "From second {start_sec} to second {curr_sec}, {audio_context}. What happened in the video is '{captions_context}'",
        ),
        MessagesPlaceholder(variable_name="history"),
        ("human", "Your friend just said this: {user_input}"),
    ]
)
memory = ConversationBufferMemory(human_prefix="Friend", return_messages=True)

# conversation chain
chat_chain = (
    RunnablePassthrough.assign(
        history=(RunnableLambda(memory.load_memory_variables) | itemgetter("history")),
    )
    | chat_prompt
    | chat_gpt
)

inputs = {
    "reactor": "iShowSpeed",
    "start_sec": start_sec,
    "curr_sec": curr_sec,
    "audio_context": audio_context,
    "captions_context": captions_context,
    "user_input": "That was an epic shot!",
}
response = chat_chain.invoke(inputs)

# update conversation memory
memory.save_context({"user_input": inputs["user_input"]}, {"output": response.content})
