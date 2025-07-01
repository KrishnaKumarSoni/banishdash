import os
from flask import Flask, render_template, request, Response, stream_template
import openai
from openai import OpenAI
import json
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# OpenAI API key
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_text():
    text = request.json.get('text', '')
    
    if not text:
        return Response(json.dumps({"error": "No text provided"}), mimetype='application/json')
    
    def generate():
        try:
            prompt = f"""Remove em dashes (—) and en dashes (–) from the following text while maintaining natural flow and readability. 
Replace these dashes with appropriate conjunctions, punctuation, or restructure sentences as needed.
Preserve all original formatting, line breaks, spacing, and paragraph structure exactly.
Only modify the parts with dashes, leave everything else unchanged.

Text to process:
{text}"""

            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                temperature=0.3
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'content': content})}\n\n"
            
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True, port=5001) 