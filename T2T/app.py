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
    if 'transcribed_text' in request.form:
        text_to_translate = request.form['transcribed_text']
    else:
        text_to_translate = request.form['text']
    target_language = request.form['target_language']
    translated_text = translate_text(text_to_translate, target_language)

    # Generate audio file
    tts = gTTS(text=translated_text, lang=target_language)
    audio_file_path = os.path.join('static', 'translated_audio.mp3')
    tts.save(audio_file_path)

    return jsonify({'translated_text': translated_text, 'audio_file_path': audio_file_path})

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']
    
    audio_path = os.path.join('static', 'uploaded_audio.wav')
    audio_file.save(audio_path)
    
    # Convert audio to text
    recognizer = sr.Recognizer()
    audio_segment = AudioSegment.from_file(audio_path)
    audio_segment.export(audio_path, format='wav')
    
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
        text_to_transcribe = recognizer.recognize_google(audio_data)
    
    return jsonify({'transcribed_text': text_to_transcribe})

@app.route('/play_audio')
def play_audio():
    audio_file_path = request.args.get('audio_file_path')
    return send_file(audio_file_path, as_attachment=True)



@app.route('/image_to_text')
def image_to_text():
    return render_template('image_to_text.html')

@app.route('/process_image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    image_file = request.files['image']
    image_path = os.path.join('static', image_file.filename)
    image_file.save(image_path)

    # Use OCR to extract text from the image
    import pytesseract
    from PIL import Image

    img = Image.open(image_path)
    extracted_text = pytesseract.image_to_string(img)

    return jsonify({'extracted_text': extracted_text, 'image_path': image_path})

@app.route('/translate_image_text', methods=['POST'])
def translate_image_text():
    text_to_translate = request.form['text']
    target_language = request.form['target_language']
    translated_text = translate_text(text_to_translate, target_language)

    # Generate audio file
    tts = gTTS(text=translated_text, lang=target_language)
    audio_file_path = os.path.join('static', 'translated_audio.mp3')
    tts.save(audio_file_path)

    return jsonify({'translated_text': translated_text, 'audio_file_path': audio_file_path})


if __name__ == '__main__':
    app.run(debug=True)
