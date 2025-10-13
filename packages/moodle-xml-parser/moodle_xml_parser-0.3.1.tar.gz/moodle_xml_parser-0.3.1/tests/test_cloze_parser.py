# File: tests/test_cloze_parser.py

import pytest
from src.moodle_xml_parser.parser import parse_string
from src.moodle_xml_parser.models import ClozeQuestion, ClozeGap, ClozeOption
from typing import List
from pprint import pprint

# 1. Define the XML content as a string (Fixture)
CLOZE_XML_CONTENT = """
<quiz>
  <question type="cloze">
    <name><text>SpongeBob's Best Friend</text></name>
    <questiontext format="html">
      <text>
        <![CDATA[ <p>Complete the sentence:</p> <p>SpongeBob's best friend is {1:SAC:=patrick~%50%patric}.</p> ]]>
      </text>
    </questiontext>
    <generalfeedback format="html"><text/></generalfeedback>
    <penalty>0.3333333</penalty>
    <hidden>0</hidden>
    <idnumber/>
  </question>
</quiz>
"""

# 2. Define a test function starting with 'test_'
def test_cloze_question_parsing():
    """Verify that a basic Cloze question is parsed correctly."""
    
    # Execute the parsing using the parse_string function
    results = parse_string(CLOZE_XML_CONTENT)

    # ----------------------------------------------------
    # STAMPA IL CONTENUTO PARSATO PER LA VERIFICA
    # ----------------------------------------------------
    cloze_questions: List[ClozeQuestion] = results.get('cloze', [])
    
    if cloze_questions:
        print("\n--- CONTENUTO CLOZE PARSATO ---")
        # Utilizza pprint per stampare la struttura degli oggetti in modo leggibile
        pprint(cloze_questions[0]) 
        print("------------------------------\n")
    # ----------------------------------------------------
    
    # 3. ASSERTIONS (Automated Checks)
    
    # A. Verify that exactly 1 cloze question is found
    cloze_questions: List[ClozeQuestion] = results.get('cloze', [])
    assert len(cloze_questions) == 1
    
    q: ClozeQuestion = cloze_questions[0]
    
    # B. Verify main question fields
    assert q.name == "SpongeBob's Best Friend"
    assert q.type == "cloze"
    assert len(q.gaps) == 1
    
    # C. Verify the GAP content (the {..} block)
    gap: ClozeGap = q.gaps[0]
    assert gap.sub_type == "SAC"
    assert gap.sub_grade == 1
    assert len(gap.options) == 2
    
    # D. Verify the OPTIONS
    option_correct: ClozeOption = gap.options[0]
    assert option_correct.answer == "patrick"
    assert option_correct.score == 100
    
    option_partial: ClozeOption = gap.options[1]
    assert option_partial.answer == "patric"
    assert option_partial.score == 50

    # If all assertions pass, the test is successful.