# File: src/moodle_xml_parser/models.py
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class Question:
    """Base class for all Moodle question types."""
    type: str # e.g., 'cloze', 'multichoice', etc.
    name: str # The short name of the question.
    text_pre_parse: str # The RAW question text, including Moodle-specific markup (e.g., the { ... } blocks for Cloze).

# --- Cloze-Specific Models ---

@dataclass
class ClozeOption:
    """Represents a single answer option within a Cloze gap."""
    answer: str
    score: int = 0
    feedback: Optional[str] = None

@dataclass
class ClozeGap:
    """Represents a single { ... } block in the Cloze question text."""
    raw_content: str # The complete text inside the curly braces: e.g., "1:SAC:=patrick~%50%patric"
    sub_type: str    # The internal sub-question type: 'SAC' (Short Answer), 'NUM' (Numerical), 'MC' (Multiple Choice), etc.
    sub_grade: int   # The relative weight/grade of the gap (usually 1)
    options: List[ClozeOption] = field(default_factory=list)
    # Additional fields for specific gap feedback can be added here if necessary

@dataclass
class ClozeQuestion(Question):
    """A complete Cloze (Embedded Answers) question."""
    gaps: List[ClozeGap] = field(default_factory=list)
    # Note: 'text_pre_parse' inherits the raw text, which includes the gap structure.

# --- Multichoice-Specific Models ---

@dataclass
class Option:
    """Represents a single answer option for a Multichoice question."""
    answer: str          # The clean option text (e.g., "<p>Run</p>")
    score_fraction: int  # The score percentage (e.g., 100 for correct, 0 for wrong, 50 for partial)
    feedback: Optional[str] = None # Specific feedback for choosing this option

@dataclass
class MultiChoiceQuestion(Question):
    """A complete Multiple Choice question."""
    # Metadata Fields
    default_grade: float
    penalty: float
    single: bool         # From <single>true/false</single> - True if single choice (radio), False if multiple choice (checkbox)
    shuffle_answers: bool # From <shuffleanswers>true/false</shuffleanswers>
    answernumbering: str # From <answernumbering> (e.g., 'abc', '123')
    
    # General Feedback Fields (Applies to the entire question based on correctness)
    general_feedback: Optional[str] = None
    correct_feedback: Optional[str] = None
    partially_correct_feedback: Optional[str] = None
    incorrect_feedback: Optional[str] = None

    # Answer Options List
    options: List[Option] = field(default_factory=list)