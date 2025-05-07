import whisper
import soundfile as sf
import torch
import os  # Add this import
import warnings

# Suppress the FutureWarning from torch.load
warnings.filterwarnings("ignore", category=FutureWarning)


# Check if GPU is available
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Load the Whisper model
model_size = "base"
model = whisper.load_model(model_size).to(device)

# Path to your .wav file
audio_file = r"D:\AI\horoscope_gen\audio_input\Liz-Training.wav"

# Read the audio file
audio, sample_rate = sf.read(audio_file)

# Transcribe the audio
result = model.transcribe(audio_file, language="en")

# Output the transcribed text
print("\nTranscribed Text:")
print(result["text"])

# Specify the directory and filename
output_dir = r"D:\AI\horoscope_gen\audio_transcription"
output_file = os.path.join(output_dir, "liz_transcription.txt")

# Create the directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Save the transcription to the file
with open(output_file, "w") as f:
    f.write(result["text"])
print(f"Transcription saved to {output_file}")