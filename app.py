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

def get_pass_prompt(pass_number, text):
    """Get the specific prompt for each pass"""
    
    if pass_number == 1:
        # Technical Cleanup
        return f"""Remove obvious AI-generated artifacts and disclosure phrases from the following text:

REMOVE these exact phrases and patterns:
- "as an AI language model", "as a large language model", "I'm sorry", "as of my last knowledge update"
- "I hope this helps", "Of course!", "Certainly!", "Would you like", "let me know", "is there anything else"
- "more detailed breakdown", collaborative communication phrases
- turn0search0, turn0search1, etc. (and any similar numbered patterns)
- contentReference[oaicite:0] and similar bracketed references
- URLs ending with ?utm_source=chatgpt.com (remove only the utm parameter)
- Fill-in-blank templates like [Entertainer's Name], [Subject Name], etc.

Preserve all original formatting, spacing, and paragraph structure. Only remove the specific AI artifacts listed above.

Text to process:
{text}"""

    elif pass_number == 2:
        # Style Normalization  
        return f"""Fix formatting and style issues typical of AI-generated text:

STYLE FIXES TO APPLY:
- Convert curly quotation marks ("" '') to straight quotes ("" '')
- Convert curly apostrophes (') to straight apostrophes (')
- Fix spaced em dashes ( — ) to unspaced em dashes (—)
- Convert Title Case Section Headings to Sentence case headings
- Remove excessive **boldface** markdown formatting (keep only essential emphasis)
- Convert markdown formatting to plain text where inappropriate
- Fix bullet points that use • or - instead of proper formatting
- Remove emoji decorations from headings (🧠, 🚨, etc.)

Preserve all content meaning and paragraph structure. Only fix formatting issues.

Text to process:
{text}"""

    elif pass_number == 3:
        # Language Refinement
        return f"""Remove promotional language, editorializing, and typical AI phrasing patterns:

LANGUAGE PATTERNS TO FIX:
- Remove/replace: "rich cultural heritage", "breathtaking", "stunning natural beauty", "must-visit", "must-see"
- Remove/replace: "stands as a testament", "plays a vital role", "underscores its importance", "continues to captivate"
- Remove/replace: "leaves a lasting impact", "watershed moment", "key turning point", "enduring legacy"
- Remove/replace: "it's important to note", "it is worth", "no discussion would be complete without"
- Remove/replace: "moreover", "furthermore", "on the other hand" (when overused)
- Remove/replace: "In summary", "In conclusion" (unless truly needed)
- Fix "not only...but also" constructions to simpler phrasing
- Remove promotional tone while keeping factual content

Make the language more neutral and encyclopedic. Preserve all facts and information.

Text to process:
{text}"""

    else:  # pass_number == 4
        # Flow Polish
        return f"""Final polish for natural flow and readability:

FINAL IMPROVEMENTS:
- Ensure smooth transitions between sentences after previous edits
- Fix any awkward phrasing created by earlier passes
- Maintain encyclopedic neutral tone
- Ensure sentences flow naturally together
- Remove any remaining repetitive or redundant phrasing
- Keep all original facts and information intact

This is the final pass - make the text read naturally while preserving all content.

Text to process:
{text}"""

@app.route('/process', methods=['POST'])
def process_text():
    text = request.json.get('text', '')
    
    if not text:
        return Response(json.dumps({"error": "No text provided"}), mimetype='application/json')
    
    def generate():
        try:
            current_text = text
            
            # Process through 4 passes
            for pass_num in range(1, 5):
                # Send pass status
                yield f"data: {json.dumps({'pass': pass_num, 'status': 'starting'})}\n\n"
                
                prompt = get_pass_prompt(pass_num, current_text)
                
                stream = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    stream=True,
                    temperature=0.2
                )
                
                pass_result = ""
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        pass_result += content
                        yield f"data: {json.dumps({'pass': pass_num, 'content': content})}\n\n"
                
                # Update current_text for next pass
                current_text = pass_result
                
                # Send pass completion
                yield f"data: {json.dumps({'pass': pass_num, 'status': 'completed'})}\n\n"
            
            # Send final completion
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True, port=5001) 