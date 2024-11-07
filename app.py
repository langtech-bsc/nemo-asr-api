import nemo.collections.asr as nemo_asr
from fastapi import FastAPI, Request
import soundfile as sf
import io
import librosa
import numpy as np


# load model at start
model_path = "stt-ca-citrinet-512.nemo" 
asr_model = nemo_asr.models.EncDecCTCModel.restore_from(restore_path=model_path)

## API ##
app = FastAPI()
@app.get("/health")
async def get_health():
    return {"status": "healthy"}

@app.post("/")
async def transcribe_audio(request: Request):
    # Get raw audio data from request
    data = await request.body()
    
    # Read audio data
    audio_data, sample_rate = sf.read(io.BytesIO(data))
    # Convert to mono if stereo
    if len(audio_data.shape) > 1:
        audio_data = np.mean(audio_data, axis=1)
    # Resample to 16kHz if needed
    if sample_rate != 16000:
        audio_data = librosa.resample(audio_data, orig_sr=sample_rate, target_sr=16000)
    
    # Save processed audio temp and transcribe
    sf.write("temp.wav", audio_data, 16000)
    transcription = asr_model.transcribe(["temp.wav"])
    
    return {"text": transcription[0]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)