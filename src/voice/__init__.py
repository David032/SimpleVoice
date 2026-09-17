from typing import Annotated, List
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from moonshine_voice import (
    Transcriber,
    load_wav_file,
    get_model_for_language,
    TextToSpeech,
    list_tts_voices
)
import os
import wave
import struct
import time

model_path, model_arch = get_model_for_language("en")
transcriber = Transcriber(model_path=model_path, model_arch=model_arch)
tts = TextToSpeech().language("en")

# Get project root directory
project_root = os.path.dirname(os.path.abspath(__file__))
project_dir = project_root[:-9]


tts.voice("zipvoice_new_zealand_female")

tts.load()

def transcribe(transcriber: Transcriber, audio_data: List[float], sample_rate: int):
    transcript = transcriber.transcribe_without_streaming(audio_data, sample_rate=sample_rate, flags=0)
    return transcript

app = FastAPI()

@app.get("/ping")
def read_root():
    return "online"


@app.post("/speech")
async def convert_speech_to_text(file: UploadFile):
    if file.content_type != "audio/wav":
        return {"error": "Invalid file type. Please upload a WAV file."}
    else:
        if not os.path.isdir("tmp"):
            os.makedirs("tmp")

        # Save the uploaded file to a temporary location
        temp_file_path = f"tmp/{file.filename}"
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(await file.read())
        
        audio_data, sample_rate = load_wav_file(temp_file_path)
        transcript = transcribe(transcriber, audio_data, sample_rate=sample_rate)
        generated_text = ""
        for line in transcript.lines:
            generated_text += line.text + " "

        os.remove(temp_file_path)  # Clean up the temporary file

        return {"generated_text": generated_text}

def save_tuple_to_wav(audio_tuple, output_filename):
    """
    Converts a tuple containing (float_samples_list, sample_rate) into a 16-bit WAV file.
    
    :param audio_tuple: A tuple structured as (list_of_floats, int_sample_rate)
    :param output_filename: Path to the target .wav file
    """
    # 1. Unpack the tuple directly
    float_samples, sample_rate = audio_tuple
    
    int_samples = []
    
    # 2. Scale and clip float samples (-1.0 to 1.0) into 16-bit integers
    for sample in float_samples:
        scaled = int(sample * 32767.0)
        clipped = max(-32768, min(32767, scaled))  # Prevent audio clipping overflow
        int_samples.append(clipped)
        
    # 3. Write to WAV
    with wave.open(output_filename, 'wb') as wav_file:
        n_channels = 1       # 1 for Mono, 2 for Stereo
        sample_width = 2     # 2 bytes = 16-bit audio
        num_frames = len(int_samples)
        
        wav_file.setparams((n_channels, sample_width, sample_rate, num_frames, 'NONE', 'not compressed'))
        
        # Pack as signed 16-bit shorts ('h')
        packed_data = struct.pack(f"{num_frames}h", *int_samples)
        wav_file.writeframes(packed_data)

@app.post("/text")
async def convert_text_to_speech(text: str):
    pcm_data = tts.synthesize(text)
    # Save the generated speech to a temporary WAV file
    timestamp = int(time.time())
    filename = f"generated_speech_{timestamp}.wav"
    temp_file_path = f"tmp/{filename}"
    if not os.path.isdir("tmp"):
        os.makedirs("tmp")    

    save_tuple_to_wav(pcm_data, temp_file_path)

    return FileResponse(temp_file_path, media_type="audio/wav", filename=filename)

def main() -> None:
    print("Hello from voice!")