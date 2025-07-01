# BanishDash

A simple, effective tool that removes em dashes from text while maintaining natural flow and exact formatting.

## Features

- Removes em dashes intelligently using GPT-4o-mini
- Maintains original text formatting and structure
- Real-time streaming output
- Clean, minimalistic interface
- Copy to clipboard functionality

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/banishdash.git
cd banishdash
```

2. Create virtual environment and install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Create `.env` file with your OpenAI API key:
```bash
OPENAI_API_KEY=your_openai_api_key_here
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and go to `http://localhost:5000`

## Deployment

This app is configured for Vercel deployment:

1. Install Vercel CLI: `npm i -g vercel`
2. Login: `vercel login`
3. Deploy: `vercel`
4. Set environment variable `OPENAI_API_KEY` in Vercel dashboard

## Usage

1. Paste your text containing em dashes into the input area
2. Click "Process Text"
3. Watch as the processed text streams in real-time
4. Copy the result to your clipboard when done

The tool intelligently replaces em dashes with appropriate conjunctions, punctuation, or restructures sentences as needed while preserving all original formatting. 