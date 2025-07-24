"""
AI Text Humanizer - Text Processing Module
Evidence-based approach combining regex preprocessing + AI transformation + post-processing
"""

import re
from typing import Dict, List, Tuple

class TextProcessor:
    """
    Research-backed text processor for AI content humanization
    Based on Wikipedia AI catchphrases analysis and GitHub best practices
    """
    
    def __init__(self):
        # Character normalization mappings (from research)
        self.char_mappings = {
            # Em/En dashes to hyphens (critical for AI consistency)
            '—': '-',  # em dash
            '–': '-',  # en dash  
            '−': '-',  # minus sign
            '‐': '-',  # hyphen variant
            '~': '-',  # tilde (when used as dash)
            
            # Curly quotes to straight (AI-text-sanitizer pattern)
            '"': '"', '"': '"',  # curly double quotes
            ''': "'", ''': "'",  # curly single quotes
            
            # Other common AI artifacts
            '…': '...',  # ellipsis
            '•': '*',    # bullet point
        }
        
        # Technical artifacts (from Wikipedia analysis)
        self.technical_patterns = [
            r'turn0search\d+',
            r'turn0image\d+',
            r'citeturn0search\d+',
            r':contentReference\[oaicite:\d+\]\{index=\d+\}',
            r'\?utm_source=chatgpt\.com',
            r'iturn0image\d+',
        ]
        
        # AI disclosure phrases (immediate removal)
        self.disclosure_patterns = [
            r'\bas an AI language model[^.]*\.?',
            r'\bas a large language model[^.]*\.?',
            r'\bI\'m sorry[^.]*AI[^.]*\.?',
            r'\bas of my last knowledge update[^.]*\.?',
            r'\bI don\'t have specific information[^.]*\.?',
        ]
        
        # Collaborative phrases (conversational artifacts)
        self.collaborative_patterns = [
            r'\bI hope this helps\.?',
            r'\bOf course!',
            r'\bCertainly!',
            r'\bWould you like me to[^.]*\?',
            r'\bLet me know if[^.]*\.?',
            r'\bIs there anything else[^.]*\?',
            r'\bFeel free to[^.]*\.?',
        ]
    
    def pre_process(self, text: str) -> Dict[str, any]:
        """
        Pre-processing: deterministic fixes for obvious AI artifacts
        Returns: {cleaned_text, stats}
        """
        original_text = text
        changes = []
        
        # 1. Character normalization (highest priority)
        for old_char, new_char in self.char_mappings.items():
            if old_char in text:
                count = text.count(old_char)
                text = text.replace(old_char, new_char)
                changes.append(f"Normalized {count} '{old_char}' → '{new_char}'")
        
        # 2. Remove technical artifacts
        for pattern in self.technical_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)
                changes.append(f"Removed {len(matches)} technical artifacts: {pattern}")
        
        # 3. Remove AI disclosure phrases  
        for pattern in self.disclosure_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)
                changes.append(f"Removed {len(matches)} disclosure phrases")
        
        # 4. Remove collaborative phrases
        for pattern in self.collaborative_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)
                changes.append(f"Removed {len(matches)} collaborative phrases")
        
        # 5. Clean up whitespace
        text = re.sub(r'\s+', ' ', text)  # collapse multiple spaces
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # max 2 line breaks
        text = text.strip()
        
        return {
            'text': text,
            'changes': changes,
            'reduction_ratio': 1 - (len(text) / len(original_text)) if original_text else 0
        }
    
    def post_process(self, text: str) -> Dict[str, any]:
        """
        Post-processing: safety net for AI model inconsistencies
        Handles cases where AI ignores constraints
        """
        original_text = text
        fixes = []
        
        # 1. Emergency dash fixes (for stubborn AI)
        em_dash_count = text.count('—')
        en_dash_count = text.count('–')
        
        if em_dash_count > 0 or en_dash_count > 0:
            # Smart replacement preserving sentence flow
            # "word — word" → "word, word"
            text = re.sub(r'(\w+)\s*[—–]\s*(\w+)', r'\1, \2', text)
            
            # "sentence — Sentence" → "sentence. Sentence"  
            text = re.sub(r'(\w+)\s*[—–]\s*([A-Z]\w+)', r'\1. \2', text)
            
            # Cleanup any remaining dashes
            text = text.replace('—', '-').replace('–', '-')
            
            fixes.append(f"Fixed {em_dash_count + en_dash_count} stubborn dashes")
        
        # 2. Quote consistency check
        curly_quotes = len(re.findall(r'[""'']', text))
        if curly_quotes > 0:
            text = text.replace('"', '"').replace('"', '"')
            text = text.replace(''', "'").replace(''', "'")
            fixes.append(f"Fixed {curly_quotes} curly quotes")
        
        # 3. Remove any remaining AI artifacts that slipped through
        remaining_artifacts = re.findall(r'turn0\w+\d+|:contentReference|\?utm_source=chatgpt', text)
        if remaining_artifacts:
            for artifact in remaining_artifacts:
                text = text.replace(artifact, '')
            fixes.append(f"Removed {len(remaining_artifacts)} remaining artifacts")
        
        # 4. Final cleanup
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return {
            'text': text,
            'fixes': fixes,
            'was_dirty': len(fixes) > 0
        }
    
    def get_humanization_prompt(self, preprocessed_text: str) -> str:
        """
        Engineering-optimized prompt for single-pass humanization
        Based on successful industry patterns
        """
        return f"""Transform this AI-generated text into natural, human-written content.

CRITICAL CONSTRAINTS (you MUST follow these exactly):
• Use only straight quotes ("word") never curly quotes ("word")
• Use only regular hyphens (-) never em dashes (—) or en dashes (–)  
• Use only straight apostrophes (') never curly ones (')

CONTENT IMPROVEMENTS:
• Replace promotional language: "breathtaking", "rich heritage", "must-visit" → neutral descriptions
• Remove editorializing: "it's important to note", "it is worth mentioning" → direct statements
• Remove puffery: "stands as a testament", "plays a vital role" → simple facts
• Remove summary phrases: "In conclusion", "In summary" → natural transitions
• Fix "not only...but also" constructions → simpler phrasing

STYLE REQUIREMENTS:
• Conversational, natural flow
• Varied sentence lengths (avoid AI uniformity)
• Remove overly formal academic tone
• Preserve all factual information and meaning
• Keep original paragraph structure

TEXT TO TRANSFORM:
{preprocessed_text}

HUMANIZED OUTPUT (following ALL constraints above):"""