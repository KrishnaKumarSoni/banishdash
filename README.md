# Kleantype

A comprehensive AI text cleaner that removes AI-generated catchphrases, fixes formatting issues, and improves readability through intelligent multi-pass processing.

## Features

- **4-pass AI cleaning system** using GPT-4o-mini
  - Pass 1: Remove technical AI artifacts and disclosure phrases
  - Pass 2: Fix formatting and style issues 
  - Pass 3: Remove promotional language and editorializing
  - Pass 4: Polish flow and readability
- **Real-time streaming** output with progress indicators
- **Maintains original formatting** and structure
- **Clean, minimalistic interface** with font toggle
- **Copy to clipboard** functionality
- **Progress tracking** through all cleaning passes

## What It Removes

Based on Wikipedia's comprehensive AI catchphrase guide, Kleantype removes:
- AI disclosure phrases ("as an AI language model", "I hope this helps")
- Technical artifacts (turn0search0, contentReference patterns)
- Promotional language ("rich cultural heritage", "breathtaking")
- Editorializing phrases ("it's important to note", "moreover")
- Style issues (curly quotes, excessive boldface, emoji headers)
- Flow problems and redundant phrasing

## Setup

1. Clone the repository:
```bash
git clone https://github.com/KrishnaKumarSoni/banishdash.git
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

5. Open your browser and go to `http://localhost:5001`

## Deployment

This app is configured for Vercel deployment:

1. Install Vercel CLI: `npm i -g vercel`
2. Login: `vercel login`
3. Deploy: `vercel`
4. Set environment variable `OPENAI_API_KEY` in Vercel dashboard

## Usage

1. Paste your AI-generated text into the input area
2. Click "Clean Text"
3. Watch as the text is processed through 4 cleaning passes with real-time progress
4. Copy the cleaned, natural-sounding result to your clipboard

Kleantype systematically removes AI artifacts while preserving all factual content and maintaining natural readability. 