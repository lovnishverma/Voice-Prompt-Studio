import os
import tempfile
import requests
import logging
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv

# Try to import pydub for audio chunking
try:
    from pydub import AudioSegment
    HAS_PYDUB = True
except ImportError:
    HAS_PYDUB = False

load_dotenv()

# Set up logging for the dynamic model selector
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Restrict max upload size to 32MB to prevent memory exhaustion
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

SARVAM_API_URL = "https://api.sarvam.ai/speech-to-text"

def get_available_model_name(api_key):
    """
    Dynamically finds a working model from the user's account using the REST API.
    Adapted to be thread-safe for dynamic per-request API keys.
    """
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        resp = requests.get(url, timeout=10)
        
        if resp.status_code != 200:
            logger.error(f"Failed to list models: {resp.text}")
            # Fallback to the most likely stable alias if the list request fails
            return "models/gemini-1.5-flash"
            
        data = resp.json()
        available_models = []
        
        for m in data.get('models', []):
            if 'generateContent' in m.get('supportedGenerationMethods', []):
                available_models.append(m.get('name'))

        if not available_models:
            logger.error("No models found.")
            return None

        # Priority list: Try to find these specific powerful models first
        preferred_order = [
            "models/gemini-1.5-flash",
            "models/gemini-1.5-pro",
            "models/gemini-pro",
            "models/gemini-1.0-pro"
        ]
        
        # 1. Check if any preferred model is in the available list
        for preferred in preferred_order:
            if preferred in available_models:
                logger.info(f"Selected Preferred Model: {preferred}")
                return preferred

        # 2. If none of the preferred ones exist, take the first available one
        fallback = available_models[0]
        logger.warning(f"Preferred models missing. Falling back to: {fallback}")
        return fallback

    except Exception as e:
        logger.error(f"Error listing models: {e}")
        return "models/gemini-1.5-flash" # Safe default


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/transcribe', methods=['POST'])
def transcribe():
    # Cascade: Use client key if provided, fallback to environment variable
    sarvam_key = os.getenv("SARVAM_API_KEY")
    language = request.form.get('language', 'en-IN')

    if not sarvam_key:
        return jsonify({'error': 'Sarvam API key is required. Provide it in the UI or set SARVAM_API_KEY env var.'}), 401

    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided in request.'}), 400

    file = request.files['audio']
    if file.filename == '':
        return jsonify({'error': 'No file selected.'}), 400

    # Ephemeral file handling
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_audio:
            file.save(temp_audio.name)
            temp_filepath = temp_audio.name

        # --- CHUNKING LOGIC FOR AUDIO > 30s ---
        if HAS_PYDUB:
            try:
                audio = AudioSegment.from_file(temp_filepath)
                chunk_length_ms = 29 * 1000 # 29 seconds (safe margin below 30s)
                
                # If audio is longer than 29s, process in chunks
                if len(audio) > chunk_length_ms:
                    chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
                    full_transcript = []
                    
                    for i, chunk in enumerate(chunks):
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as chunk_file:
                            chunk.export(chunk_file.name, format="wav")
                            
                            with open(chunk_file.name, 'rb') as f:
                                files = {'file': (f"chunk_{i}.wav", f, 'audio/wav')}
                                data = {
                                    'language_code': language,
                                    'model': 'saarika:v2.5',
                                    'with_timestamps': 'false'
                                }
                                headers = {'api-subscription-key': sarvam_key}
                                
                                response = requests.post(
                                    SARVAM_API_URL,
                                    headers=headers,
                                    files=files,
                                    data=data,
                                    timeout=60
                                )
                        os.remove(chunk_file.name)
                        
                        if response.status_code == 200:
                            result = response.json()
                            transcript = result.get('transcript') or result.get('text') or ''
                            if transcript:
                                full_transcript.append(transcript.strip())
                        else:
                            # Clean up and bubble error if any chunk fails
                            os.remove(temp_filepath)
                            try:
                                err_msg = response.json().get('message', response.text)
                            except ValueError:
                                err_msg = response.text
                            return jsonify({'error': f'Sarvam API error on chunk {i+1}: {err_msg}'}), response.status_code
                    
                    os.remove(temp_filepath)
                    return jsonify({'success': True, 'transcript': " ".join(full_transcript)})

            except Exception as e:
                logger.warning(f"Pydub chunking failed (ffmpeg likely missing): {e}. Falling back to direct upload.")
                pass # Proceed to direct upload fallback

        # --- DIRECT UPLOAD FALLBACK (For <30s files or missing ffmpeg) ---
        with open(temp_filepath, 'rb') as f:
            files = {'file': (file.filename, f, file.mimetype or 'audio/webm')}
            data = {
                'language_code': language,
                'model': 'saarika:v2.5',
                'with_timestamps': 'false'
            }
            headers = {'api-subscription-key': sarvam_key}
            
            response = requests.post(
                SARVAM_API_URL,
                headers=headers,
                files=files,
                data=data,
                timeout=60
            )

        os.remove(temp_filepath)

        if response.status_code == 200:
            result = response.json()
            transcript = result.get('transcript') or result.get('text') or ''
            return jsonify({'success': True, 'transcript': transcript})
        else:
            try:
                err_msg = response.json().get('message', response.text)
            except ValueError:
                err_msg = response.text
                
            # Intercept the specific 30s limit error to guide the user to the fix
            if "duration exceeds" in err_msg.lower() or "30 seconds" in err_msg.lower():
                return jsonify({'error': 'Audio > 30s. To enable automatic chunking, run: "pip install pydub" AND install ffmpeg on your server.'}), 400
                
            return jsonify({'error': f'Sarvam API error: {err_msg}'}), response.status_code

    except Exception as e:
        if 'temp_filepath' in locals() and os.path.exists(temp_filepath):
            os.remove(temp_filepath)
        return jsonify({'error': f'Transcription processing failed: {str(e)}'}), 500


@app.route('/refine', methods=['POST'])
def refine():
    data = request.get_json() or {}
    gemini_key = os.getenv("GEMINI_API_KEY")
    transcript = data.get('transcript', '').strip()
    tone = data.get('tone', 'clear')

    if not gemini_key:
        return jsonify({'error': 'Gemini API key is required. Provide it in the UI or set GEMINI_API_KEY env var.'}), 401

    if not transcript:
        return jsonify({'error': 'No transcript provided for refinement.'}), 400

    # Dynamically select the best model based on the provided API key
    model_name = get_available_model_name(gemini_key)
    if not model_name:
        return jsonify({'error': 'No suitable Gemini models found for this API key.'}), 500

    dynamic_gemini_url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent"

    tone_instructions = {
        'clear': 'Refine into a clear, direct, and well-structured prompt. Remove filler words while preserving the original intent.',
        'detailed': 'Act as an expert prompt engineer. Expand this raw idea into a highly detailed, comprehensive prompt. Flesh out implicit requirements. Include specific structured sections such as: [Objective], [Target Audience], [Core Features], and [Technical Constraints]. Ensure the resulting prompt leaves no ambiguity.',
        'concise': 'Distill this into an ultra-concise, powerful AI prompt containing only the essential keywords and core intent.',
        'creative': 'Transform this into a creative AI prompt, suggesting innovative angles, vivid language, and out-of-the-box features related to the core idea.',
        'technical': 'Convert this into a precise, highly technical prompt suitable for a senior engineer. Explicitly propose appropriate domain terminology, specific tech stacks, data models, or algorithms (e.g., recommendation engines, APIs) relevant to the idea.',
        'step-by-step': 'Structure the AI prompt as a comprehensive series of actionable, numbered implementation phases.'
    }

    instruction = tone_instructions.get(tone, tone_instructions['clear'])

    system_prompt = (
        "You are a Master Prompt Engineer. The user will provide a raw, unstructured voice transcript of an idea.\n"
        "Your ONLY job is to write a professional, highly effective prompt based on their idea that they can feed into another AI to build or execute their vision.\n"
        "Do NOT answer or fulfill their idea yourself. Just write the expansive prompt FOR them.\n"
        f"Style and Structure Directive: {instruction}\n"
        "IMPORTANT RULES:\n"
        "1. Return ONLY the final generated prompt.\n"
        "2. Do NOT include any conversational filler (e.g., 'Here is your prompt:').\n"
        "3. Do NOT wrap your entire response in a global markdown code block (like ```markdown), but you MAY use internal markdown like bolding, lists, and headings to structure the prompt thoroughly.\n"
        "4. CRITICAL: Ensure the response is completely finished and fully fleshed out. DO NOT truncate or cut off mid-sentence."
    )

    headers = {"Content-Type": "application/json"}
    
    # Merged system_prompt directly into the user contents block to ensure schema compatibility
    payload = {
        "contents": [
            {
                "role": "user", 
                "parts": [{"text": f"{system_prompt}\n\n---\nRaw Voice Transcript:\n{transcript}"}]
            }
        ],
        "generationConfig": {
            "temperature": 0.8, 
            "maxOutputTokens": 8192 # Tripled max tokens to prevent truncation on extremely detailed responses
        }
    }

    try:
        # Extended timeout to 60s to accommodate massive generated prompts
        resp = requests.post(
            f"{dynamic_gemini_url}?key={gemini_key}",
            headers=headers,
            json=payload,
            timeout=60
        )

        if resp.status_code != 200:
            try:
                err_msg = resp.json().get("error", {}).get("message", resp.text)
            except ValueError:
                err_msg = resp.text
            return jsonify({'error': f'Gemini API error: {err_msg}'}), resp.status_code

        result = resp.json()
        refined = (
            result.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [{}])[0]
            .get("text", "")
            .strip()
        )

        if not refined:
            return jsonify({'error': 'Empty response from Gemini API. The model returned no text.'}), 500

        return jsonify({'success': True, 'prompt': refined})

    except requests.exceptions.Timeout:
        return jsonify({'error': 'Gemini API request timed out while generating a response.'}), 504
    except Exception as e:
        return jsonify({'error': f'Refinement processing failed: {str(e)}'}), 500


if __name__ == '__main__':
    # Make sure 'templates' folder exists in the same directory as app.py
    app.run(debug=True, port=5000)
