import whisper

# Load the Whisper model (you can choose a different model like 'base' or 'small')
model = whisper.load_model("base")

# Transcribe the audio file
result = model.transcribe("audio.wav")

# Print the transcribed text
print(result["text"])