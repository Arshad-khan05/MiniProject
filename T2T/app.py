from flask import Flask, render_template, request, jsonify, send_file
from googletrans import Translator
from gtts import gTTS
import os
import speech_recognition as sr
from pydub import AudioSegment

app = Flask(__name__)

def translate_text(text, target_language):
    translator = Translator()
    translated_text = translator.translate(text, dest=target_language)
    return translated_text.text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/text_to_text')
def text_to_text():
    return render_template('text_to_text.html')

@app.route('/voice_to_voice')
def voice_to_voice():
    return render_template('voice_to_voice.html')

@app.route('/translate', methods=['POST'])
def translate():
    text_to_translate = request.form['text']
    target_language = request.form['target_language']
    translated_text = translate_text(text_to_translate, target_language)

    # Generate audio file
    tts = gTTS(text=translated_text, lang=target_language)
    audio_file_path = os.path.join('static', 'translated_audio.mp3')  # Use os.path.join for path concatenation
    tts.save(audio_file_path)

    return jsonify({'translated_text': translated_text, 'audio_file_path': audio_file_path})

@app.route('/voice_translate', methods=['POST'])
def voice_translate():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    target_language = request.form['target_language']
    
    audio_path = os.path.join('static', 'uploaded_audio.wav')
    audio_file.save(audio_path)
    
    # Convert audio to text
    recognizer = sr.Recognizer()
    audio_segment = AudioSegment.from_file(audio_path)
    audio_segment.export(audio_path, format='wav')
    
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
        text_to_translate = recognizer.recognize_google(audio_data)

    # Translate text
    translated_text = translate_text(text_to_translate, target_language)

    # Generate translated audio file
    tts = gTTS(text=translated_text, lang=target_language)
    translated_audio_path = os.path.join('static', 'translated_audio.mp3')
    tts.save(translated_audio_path)

    return jsonify({'translated_text': translated_text, 'audio_file_path': translated_audio_path})

@app.route('/play_audio')
def play_audio():
    audio_file_path = request.args.get('audio_file_path')
    return send_file(audio_file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
