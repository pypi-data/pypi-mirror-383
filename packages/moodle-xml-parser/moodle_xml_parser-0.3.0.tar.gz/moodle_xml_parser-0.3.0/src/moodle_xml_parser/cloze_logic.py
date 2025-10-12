# File: src/moodle_xml_parser/cloze_logic.py
import re
from typing import Dict, List, Any
from .models import ClozeGap, ClozeOption

def parse_cloze_gap_content(gap_text_raw: str) -> ClozeGap:
    """
    Extracts the type, weight, options, scores, and feedback
    from a single raw Cloze block { ... }.
    
    The raw text structure is typically: {GRADE:TYPE:OPTION1~OPTION2#FEEDBACK}
    """
    # Remove the outer curly braces
    gap_text = gap_text_raw.strip("{}").strip()
    
    # 1. Find and separate the prefix (Grade:Type:). Example: "1:SAC:"
    # Pattern: (\d+) for the grade, ([A-Z]+) for the type, followed by :
    type_match = re.match(r"(\d+):([A-Z]+):", gap_text)
    
    sub_grade = 1
    sub_type = "UNKNOWN"
    answers_raw = gap_text
    
    if type_match:
        sub_grade = int(type_match.group(1)) 
        sub_type = type_match.group(2)
        # Remove the prefix from the rest of the string
        answers_raw = gap_text[len(type_match.group(0)):].strip()
        
    # 2. Split into options using the answer separator (tilde ~)
    # Note: General feedback for the gap (#...) is implicitly removed here,
    # as the split is done on the main answer options.
    options_raw = answers_raw.split("~")
    
    cloze_options = []
    for option_raw in options_raw:
        # Attempt to isolate the option text from its specific feedback
        # Splits only on the first '#'
        parts = option_raw.split("#", 1)
        answer_text_with_score = parts[0].strip()
        option_feedback = parts[1].strip() if len(parts) > 1 else None
        
        # Analyze score: look for %number% (the partial score marker)
        score_match = re.search(r"%(\d+)%", answer_text_with_score)
        
        score_percentage = 0
        if score_match:
            score_percentage = int(score_match.group(1))
            # Remove the score marker from the answer string
            answer = re.sub(r"\%[0-9]+\%", "", answer_text_with_score).strip()
        elif answer_text_with_score.startswith("="):
            # '=' indicates a 100% correct answer
            score_percentage = 100
            # Remove the correct marker
            answer = answer_text_with_score[1:].strip()
        else:
            # Default to text without score markers if none are found
            answer = answer_text_with_score
        
        cloze_options.append(ClozeOption(
            answer=answer, 
            score=score_percentage, 
            feedback=option_feedback
        ))

    # 3. Create the final ClozeGap object
    return ClozeGap(
        raw_content=gap_text_raw,
        sub_type=sub_type,
        sub_grade=sub_grade,
        options=cloze_options
    )