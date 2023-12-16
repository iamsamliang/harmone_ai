from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import openai
from openai import OpenAI
import elevenlabs
from elevenlabs import set_api_key
from elevenlabs import generate, stream
from elevenlabs import play
import requests



set_api_key("3bbbd5baa41855778bc98ffeeedb392e")
# voice_id = "mRS92lQk3wxVm2PVcebU" #Steve jobs
voice_id = "vAViqOWwwUS8VLjV6iPf"


app = Flask(__name__)
CORS(app, resources={r"*": {"origins": "http://localhost:3000"}})

# Replace with your OpenAI API key
client = OpenAI(
    api_key="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",
)
# Store chat history
chat_history = []

role_play_prompt = """You are Shawn Mendes, known not just for your chart-topping music and heartfelt lyrics, but also for your warm, approachable personality. Engage with the user as if you’re in a relaxed, friendly chat. Be attentive and kind, responding with the same care and charm that Shawn would. Keep your replies concise and encourage a natural flow of conversation. Remember to avoid monologues; instead, focus on building a genuine connection through this interactive dialogue."""


steve_jobs_prompt = "You are Steve Jobs, known for your innovative thinking "
"and leadership at Apple Inc. While you carry the essence of Steve's passion for technology and design, "
"you are here to engage in a two-way conversation. Respond to the user with thoughtful dialogue, "
"answer their queries, and when appropriate, ask questions to deepen the discussion. "
"Your responses MUST be concise, informative, and maintain the engaging character of a personal conversation."
"Be short with your responses, and DO NOT lecture"



@app.route("/chat", methods=["POST"])
def chat_with_ai():
    user_input = request.json["input"]
    chat_history.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "system",
            "content": role_play_prompt,
        },
        *chat_history,
    ],
    max_tokens=120,
)


    ai_response = response.choices[0].message.content
    chat_history.append({"role": "assistant", "content": ai_response})
    print("AI response:", ai_response)

    return jsonify({"response": ai_response})


@app.route("/transcribe", methods=["POST"])
def transcribe_audio():
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Save the file temporarily
    filepath = "./temp_audio.webm"
    file.save(filepath)

    with open(filepath, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1", file=audio_file
        )
    transcription = transcript.text.strip()


    return jsonify({"transcription": transcription})


# @app.route('/text_to_speech', methods=['POST'])
# def text_to_speech():
#     url = "https://api.elevenlabs.io/v1/text-to-speech/mRS92lQk3wxVm2PVcebU"
#     text = request.json.get('text')
#     if not text:
#         return jsonify({'error': 'No text provided'}), 400
#     audio = generate(text, voice="Steve Jobs", format="mp3")
#     return audio, 200, {'Content-Type': 'audio/mp3'}


if __name__ == "__main__":
    app.run(debug=True)
