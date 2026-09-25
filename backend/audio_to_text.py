import os
import sys

# Ensure whisper is installed before importing
try:
    import whisper
except ImportError:
    print("Whisper is not installed. Please run: pip install -U openai-whisper")
    sys.exit(1)

def transcribe_audio(file_path):
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        return

    print(f"Loading Whisper AI model (this may take a moment on the first run)...")
    # 'base' model is small, fast, and highly accurate for English.
    # Other options: 'tiny', 'small', 'medium', 'large'
    model = whisper.load_model("base")
    
    print(f"\nStarting transcription for: {file_path}")
    print("-" * 50)
    
    try:
        # Transcribe the audio
        result = model.transcribe(file_path)
        
        # Print the result
        print("TRANSCRIPTION COMPLETE:\n")
        print(result["text"].strip())
        print("-" * 50)
        
        # Save to a text file automatically
        output_filename = os.path.splitext(file_path)[0] + "_transcription.txt"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(result["text"].strip())
            
        print(f"\nSaved successfully to: {output_filename}")
        
    except Exception as e:
        print(f"An error occurred during transcription: {e}")
        print("\nNote: You MUST have 'ffmpeg' installed on your system for Whisper to work!")

if __name__ == "__main__":
    # Example usage: python audio_to_text.py "C:\path\to\your\audio.mp3"
    if len(sys.argv) < 2:
        print("Usage: python audio_to_text.py <path_to_audio_file>")
    else:
        audio_file = sys.argv[1]
        transcribe_audio(audio_file)
