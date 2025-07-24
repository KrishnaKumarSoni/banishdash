import os
from flask import Flask, render_template, request, Response
from openai import OpenAI
import json
from dotenv import load_dotenv
from text_processor import TextProcessor
import logging

load_dotenv()

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

# Initialize OpenAI client and text processor
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
processor = TextProcessor()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process_text():
    """
    Refactored single-pass processing with evidence-based architecture
    """
    text = request.json.get('text', '').strip()
    
    if not text:
        return Response(
            json.dumps({"error": "No text provided"}), 
            mimetype='application/json'
        )
    
    def generate():
        try:
            # Phase 1: Pre-processing (deterministic fixes)
            yield f"data: {json.dumps({'pass': 1, 'status': 'analyzing', 'progress': 10, 'phase': 'analysis'})}\n\n"
            
            preprocess_result = processor.pre_process(text)
            preprocessed_text = preprocess_result['text']
            
            app.logger.info(f"Pre-processing complete. Changes: {preprocess_result['changes']}")
            
            yield f"data: {json.dumps({'pass': 1, 'status': 'completed', 'progress': 20, 'phase': 'analysis'})}\n\n"
            
            # Phase 2: AI Transformation (single call with robust constraints)
            yield f"data: {json.dumps({'pass': 5, 'status': 'consolidating', 'progress': 25, 'phase': 'consolidation'})}\n\n"
            
            # Smart retry logic: start conservative, get more aggressive if needed
            max_attempts = 2
            temperatures = [0.1, 0.05]  # Conservative → Very conservative
            
            for attempt in range(max_attempts):
                try:
                    prompt = processor.get_humanization_prompt(preprocessed_text)
                    temperature = temperatures[min(attempt, len(temperatures) - 1)]
                    
                    if attempt > 0:
                        yield f"data: {json.dumps({'pass': 5, 'status': 'retry_needed', 'reason': f'Constraint violations detected. Retrying with stricter settings...', 'progress': 30, 'phase': 'consolidation'})}\n\n"
                    
                    # Stream AI response
                    stream = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[{"role": "user", "content": prompt}],
                        stream=True,
                        temperature=temperature,
                        max_tokens=4000
                    )
                    
                    ai_output = ""
                    chunk_count = 0
                    
                    for chunk in stream:
                        if chunk.choices[0].delta.content is not None:
                            content = chunk.choices[0].delta.content
                            ai_output += content
                            chunk_count += 1
                            
                            # Progressive progress (30-90%)
                            progress = min(90, 30 + int(chunk_count / 3))
                            yield f"data: {json.dumps({'pass': 5, 'content': content, 'progress': progress, 'phase': 'consolidation'})}\n\n"
                    
                    # Check AI output quality (critical constraints)
                    constraint_violations = []
                    if '—' in ai_output:
                        constraint_violations.append('em dashes')
                    if '–' in ai_output:
                        constraint_violations.append('en dashes')
                    if any(char in ai_output for char in ['"', '"', ''', ''']):
                        constraint_violations.append('curly quotes')
                    
                    if constraint_violations and attempt < max_attempts - 1:
                        app.logger.warning(f"Attempt {attempt + 1} violated constraints: {constraint_violations}")
                        continue
                    
                    # Success or final attempt
                    break
                    
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise e
                    app.logger.error(f"AI call attempt {attempt + 1} failed: {str(e)}")
                    continue
            
            # Phase 3: Post-processing (safety net)
            postprocess_result = processor.post_process(ai_output)
            
            if postprocess_result['was_dirty']:
                app.logger.info(f"Post-processing fixes applied: {postprocess_result['fixes']}")
                yield f"data: {json.dumps({'pass': 5, 'status': 'warning', 'reason': 'Applied safety fixes for remaining issues', 'progress': 95, 'phase': 'consolidation'})}\n\n"
                # Update ai_output with post-processed version
                ai_output = postprocess_result['text']
            
            # Final completion
            yield f"data: {json.dumps({'pass': 5, 'status': 'completed', 'progress': 100, 'phase': 'completed'})}\n\n"
            yield f"data: {json.dumps({'done': True, 'progress': 100})}\n\n"
            
        except Exception as e:
            app.logger.error(f"Processing error: {str(e)}")
            yield f"data: {json.dumps({'error': f'Processing failed: {str(e)}', 'progress': 0})}\n\n"
    
    return Response(generate(), mimetype='text/plain')

if __name__ == '__main__':
    app.run(debug=True, port=5001) 