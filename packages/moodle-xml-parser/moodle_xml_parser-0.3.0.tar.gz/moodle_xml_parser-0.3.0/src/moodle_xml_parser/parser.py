# File: src/moodle_xml_parser/parser.py

import xml.etree.ElementTree as ET
import re
import html
# Import necessary types for type hinting
from typing import Dict, List, Any, Union, TextIO, BinaryIO 

# Import models and core logic from the package
from .models import ClozeQuestion, MultiChoiceQuestion, Option
from .cloze_logic import parse_cloze_gap_content

# Note: Removed 'from pprint import pprint' as it's not used in the final parser logic.

# --- Internal Core Functions ---

def _parse_to_root(source: Union[str, bytes, TextIO, BinaryIO]) -> ET.Element:
    """
    Internal function. Parses any supported XML input (string, bytes, or stream) 
    and returns the document's root element.
    """
    try:
        if isinstance(source, (str, bytes)):
            # Parse directly from string or bytes content
            return ET.fromstring(source)
        
        elif hasattr(source, 'read'):
            # Parse from a file-like object (TextIO or BinaryIO)
            return ET.parse(source).getroot()

        else:
            raise TypeError("Invalid input: must be a string, bytes object, or a readable file-like object.")
            
    except ET.ParseError as e:
        # Re-raise XML parsing errors as a ValueError for public APIs
        raise ValueError(f"XML parsing error: {e}")
    
def _parse_root_to_questions(root: ET.Element) -> Dict[str, List[Any]]:
    """Core logic for extracting questions, separated from I/O operations."""
    # Initialize dictionary to hold results, grouped by question type
    results = {"multichoice": [], "cloze": []}
    
    # Find all question nodes in the document
    for q in root.findall(".//question"):
        qtype = q.attrib.get("type")
        
        try:
            if qtype == "cloze":
                results["cloze"].append(_parse_cloze(q))
            elif qtype == "multichoice":
                results["multichoice"].append(_parse_multichoice(q))
            # Add 'elif qtype == "new_type":' for future question types
            
        except Exception as e:
            # Print error and continue parsing other questions
            print(f"Error while parsing question type '{qtype}': {e}")

    return results

# --- Public API Functions (I/O Handlers) ---

def parse_file(file_path: str) -> Dict[str, List[Any]]:
    """
    Parses a Moodle XML file specified by its file path.
    Ideal for local use or command-line tools.
    """
    # Open file in binary read mode ('rb') for compatibility with ET.parse
    with open(file_path, 'rb') as f:
        root = _parse_to_root(f)
    return _parse_root_to_questions(root)

def parse_string(xml_string: str) -> Dict[str, List[Any]]:
    """
    Parses a text string containing the entire Moodle XML content.
    Ideal for use in web backends (with decoded data).
    """
    root = _parse_to_root(xml_string)
    return _parse_root_to_questions(root)

def parse_bytes(byte_stream: Union[bytes, BinaryIO]) -> Dict[str, List[Any]]:
    """
    Parses a stream of bytes (bytes object) or a binary file-like object 
    (e.g., an uploaded file in memory).
    """
    root = _parse_to_root(byte_stream)
    return _parse_root_to_questions(root)

# --- Utility Functions ---

def _extract_text_content(node: ET.Element) -> str:
    """Extracts text from a <text> node, removing CDATA wrappers and unescaping HTML entities."""
    if node is None or node.text is None:
        return ""
    text = node.text.strip()
    # Remove CDATA start/end markers
    text = re.sub(r"<!\[CDATA\[|\]\]>", "", text)
    # Decode HTML entities (like &nbsp;)
    return html.unescape(text)

# --- Question-Specific Parsers ---

def _parse_cloze(xml_question: ET.Element) -> ClozeQuestion:
    """
    Parses a 'cloze' XML block, extracting name, raw text, and deconstructing 
    all the { ... } response blocks within it.
    """
    
    # 1. Extract Question Name
    name_el = xml_question.find("./name/text")
    name = _extract_text_content(name_el) if name_el is not None else "Unnamed Cloze"
    
    # 2. Extract RAW Question Text (contains the {...} blocks)
    text_el = xml_question.find("./questiontext/text")
    text_raw = _extract_text_content(text_el) if text_el is not None else ""
    
    # 3. Find and Parse all Cloze Gaps
    
    # Pattern to find all { ... } blocks including their content
    cloze_pattern = r"\{.*?}"
    raw_gaps = re.findall(cloze_pattern, text_raw)
    
    gaps_parsed = []
    for raw_gap_string in raw_gaps:
        try:
            # Use the dedicated parsing logic from cloze_logic.py
            gap_object = parse_cloze_gap_content(raw_gap_string)
            gaps_parsed.append(gap_object)
        except Exception as e:
            # Error handling for malformed {..} markup
            print(f"Error parsing cloze gap: '{raw_gap_string}'. Error: {e}")
            
    # 4. Create the final ClozeQuestion object
    return ClozeQuestion(
        type="cloze",
        name=name,
        text_pre_parse=text_raw,
        gaps=gaps_parsed
    )

def _parse_option(xml_answer: ET.Element) -> Option:
    """Parses a single <answer> block and returns an Option object."""
    
    # 1. Extract the score fraction
    # The 'fraction' attribute is read as a string (e.g., "100" or "0")
    score = int(xml_answer.attrib.get('fraction', '0'))
    
    # 2. Extract the option text
    text_el = xml_answer.find("./text")
    answer_text = _extract_text_content(text_el)
    
    # 3. Extract the option-specific feedback
    feedback_el = xml_answer.find("./feedback/text")
    option_feedback = _extract_text_content(feedback_el) if feedback_el is not None else None
    
    return Option(
        answer=answer_text,
        score_fraction=score,
        feedback=option_feedback
    )

def _parse_multichoice(xml_question: ET.Element) -> MultiChoiceQuestion:
    """Parses a 'multichoice' XML block."""
    
    # 1. Extract Common Metadata
    name_el = xml_question.find("./name/text")
    name = _extract_text_content(name_el) if name_el is not None else "Unnamed Multichoice"
    
    text_el = xml_question.find("./questiontext/text")
    text_pre_parse = _extract_text_content(text_el) if text_el is not None else ""
    
    # 2. Extract Specific Multichoice Metadata
    
    # Convert 'true'/'false' strings to native booleans
    single_str = xml_question.findtext("./single", "true").lower()
    shuffle_str = xml_question.findtext("./shuffleanswers", "false").lower()

    default_grade = float(xml_question.findtext("./defaultgrade", "1.0"))
    penalty = float(xml_question.findtext("./penalty", "0.0"))
    
    # 3. Extract General Feedback
    general_feedback_el = xml_question.find("./generalfeedback/text")
    correct_feedback_el = xml_question.find("./correctfeedback/text")
    partially_correct_feedback_el = xml_question.find("./partiallycorrectfeedback/text")
    incorrect_feedback_el = xml_question.find("./incorrectfeedback/text")
    
    # 4. Extract All Answer Options
    options = []
    for answer_el in xml_question.findall("./answer"):
        options.append(_parse_option(answer_el))
        
    # 5. Create the Final Object
    return MultiChoiceQuestion(
        type="multichoice",
        name=name,
        text_pre_parse=text_pre_parse,
        default_grade=default_grade,
        penalty=penalty,
        single=(single_str == 'true'),
        shuffle_answers=(shuffle_str == 'true'),
        answernumbering=xml_question.findtext("./answernumbering", "abc"),
        
        general_feedback=_extract_text_content(general_feedback_el),
        correct_feedback=_extract_text_content(correct_feedback_el),
        partially_correct_feedback=_extract_text_content(partially_correct_feedback_el),
        incorrect_feedback=_extract_text_content(incorrect_feedback_el),
        
        options=options
    )