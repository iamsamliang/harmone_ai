# harmone_ai
AI Companion that watches YouTube with you and reacts to video content and what you say in real-time

Run ```python pipeline.py``` to:
1. Download video and audio
2. Extract video metadata
3. Convert audio to text and store it in pinecone
4. Convert video to frames
5. Convert frames to captions and store in PostgreSQL database along with video metadata

Specify parameters in ```pipeline.py```, specifically the YouTube URL and the output filename
