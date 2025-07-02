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

def get_analysis_prompt(pass_number, text):
    """Get the analysis prompt for each pass - identifies issues without fixing them"""
    
    if pass_number == 1:
        # Technical Cleanup Analysis
        return f"""Analyze the following text and identify all AI-generated artifacts and disclosure phrases. DO NOT fix them, just list what you find:

IDENTIFY these patterns (list specific instances found):
- AI disclosure phrases: "as an AI language model", "as a large language model", "I'm sorry", "as of my last knowledge update"
- Collaborative phrases: "I hope this helps", "Of course!", "Certainly!", "Would you like", "let me know", "is there anything else"
- Technical artifacts: turn0search0, turn0search1, contentReference[oaicite:0], URLs with utm_source=chatgpt.com
- Template placeholders: [Entertainer's Name], [Subject Name], etc.

Format your response as a structured list of issues found. Be specific about what phrases or patterns you detected.

Text to analyze:
{text}"""

    elif pass_number == 2:
        # Style Analysis
        return f"""Analyze the following text for formatting and style issues typical of AI-generated content. DO NOT fix them, just identify what needs correction:

IDENTIFY these formatting issues (list specific instances):
- Curly quotation marks ("" '') that should be straight quotes
- Curly apostrophes (') that should be straight
- Spaced em dashes ( — ) that should be unspaced (—)
- Title Case Headings that should be sentence case
- Excessive **boldface** markdown formatting
- Inappropriate markdown formatting
- Bullet points using • or - instead of proper formatting
- Emoji decorations in headings (🧠, 🚨, etc.)

List the specific formatting problems you identify.

Text to analyze:
{text}"""

    elif pass_number == 3:
        # Language Analysis
        return f"""Analyze the following text for promotional language, editorializing, and typical AI phrasing patterns. DO NOT fix them, just identify what needs improvement:

IDENTIFY these language issues (list specific instances):
- Promotional phrases: "rich cultural heritage", "breathtaking", "stunning natural beauty", "must-visit"
- Puffery: "stands as a testament", "plays a vital role", "continues to captivate", "leaves a lasting impact"
- Editorializing: "it's important to note", "it is worth", "no discussion would be complete"
- Overused conjunctives: "moreover", "furthermore", "on the other hand"
- Summary clichés: "In summary", "In conclusion"
- Awkward constructions: "not only...but also" patterns

List the specific language problems and suggest better alternatives.

Text to analyze:
{text}"""

    else:  # pass_number == 4
        # Flow Analysis
        return f"""Analyze the text for flow and readability issues. DO NOT fix them, just identify areas that need improvement:

IDENTIFY these flow issues:
- Awkward transitions between sentences
- Repetitive or redundant phrasing
- Sentences that don't flow naturally together
- Unclear connections between ideas
- Any remaining verbose or unnatural language patterns

List specific areas where flow could be improved.

Text to analyze:
{text}"""

def get_consolidation_prompt(original_text, insights):
    """Create the final consolidation prompt with original text and all insights"""
    
    insights_text = "\n\n".join([f"PASS {i+1} FINDINGS:\n{insight}" for i, insight in enumerate(insights)])
    
    return f"""You are a text editor tasked with cleaning up AI-generated artifacts while preserving all original meaning and information.

ORIGINAL TEXT:
{original_text}

ANALYSIS FROM SPECIALIZED PASSES:
{insights_text}

INSTRUCTIONS:
Based on the analysis above, clean up the original text by addressing the identified issues. Your goals:

1. Remove AI disclosure phrases and technical artifacts
2. Fix formatting and style issues  
3. Replace promotional/editorializing language with neutral alternatives
4. Improve flow and readability
5. PRESERVE all factual content, meaning, and structure
6. MAINTAIN the original formatting and paragraph breaks

Output the cleaned text directly. Be thorough but conservative - only change what's clearly problematic based on the analysis."""

@app.route('/process', methods=['POST'])
def process_text():
    text = request.json.get('text', '')
    
    if not text:
        return Response(json.dumps({"error": "No text provided"}), mimetype='application/json')
    
    def generate():
        try:
            original_text = text
            insights = []
            
            # Analysis Phase: Collect insights from each pass
            for pass_num in range(1, 5):
                # Send pass status
                yield f"data: {json.dumps({'pass': pass_num, 'status': 'analyzing'})}\n\n"
                
                prompt = get_analysis_prompt(pass_num, original_text)
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1
                )
                
                insight = response.choices[0].message.content
                insights.append(insight)
                
                # Stream the analysis results
                yield f"data: {json.dumps({'pass': pass_num, 'content': f'✓ Analysis complete', 'analysis': insight})}\n\n"
                yield f"data: {json.dumps({'pass': pass_num, 'status': 'completed'})}\n\n"
            
            # Consolidation Phase: Apply all fixes with fresh LLM instance
            yield f"data: {json.dumps({'pass': 5, 'status': 'consolidating'})}\n\n"
            
            consolidation_prompt = get_consolidation_prompt(original_text, insights)
            
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": consolidation_prompt}],
                stream=True,
                temperature=0.2
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'pass': 5, 'content': content})}\n\n"
            
            # Send final completion
            yield f"data: {json.dumps({'pass': 5, 'status': 'completed'})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return Response(generate(), mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True, port=5001) 