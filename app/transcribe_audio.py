import base64
import whisper
import os
import uuid
from pydub import AudioSegment


def transcribe(base64_audio):
    # Generate a random filename
    temp_filename = f"/tmp/{uuid.uuid4()}"
    ogg_file = f"{temp_filename}.ogg"
    wav_file = f"{temp_filename}.wav"

    try:
        decoded_audio = base64.b64decode(base64_audio)
        with open(ogg_file, 'wb') as f:
            f.write(decoded_audio)
        
        audio = AudioSegment.from_ogg(ogg_file)
        audio.export(wav_file, format='wav')
        
        print("loading model...")
        model = whisper.load_model("base")
        print("model loaded!")
        
        result = model.transcribe(wav_file)
        return result['text']
    
    finally:
        # Clean up temporary files
        for file in [ogg_file, wav_file]:
            if os.path.exists(file):
                os.remove(file)
