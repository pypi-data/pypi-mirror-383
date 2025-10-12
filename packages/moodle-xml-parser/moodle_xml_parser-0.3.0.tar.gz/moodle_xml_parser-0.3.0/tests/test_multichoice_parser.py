# File: tests/test_multichoice_parser.py

import pytest
from src.moodle_xml_parser.parser import parse_string
from src.moodle_xml_parser.models import MultiChoiceQuestion, Option
from typing import List

# 1. XML content for the Multichoice test question (Fixture)
MULTICHOICE_XML_CONTENT = """
<quiz>
<question type="multichoice">
<name>
<text>Which of these is a verb?</text>
</name>
<questiontext format="html">
<text>
<![CDATA[ <p>Indicate which of the following words is a verb.</p> ]]>
</text>
</questiontext>
<generalfeedback format="html">
<text>
<![CDATA[ <p>- test: general feedback -</p> ]]>
</text>
</generalfeedback>
<defaultgrade>1</defaultgrade>
<penalty>0.3333333</penalty>
<hidden>0</hidden>
<single>true</single>
<shuffleanswers>true</shuffleanswers>
<answernumbering>abc</answernumbering>
<correctfeedback format="html">
<text><![CDATA[ <p>Your answer is correct.</p> ]]></text>
</correctfeedback>
<incorrectfeedback format="html">
<text><![CDATA[ <p>Your answer is incorrect.</p> ]]></text>
</incorrectfeedback>
<answer fraction="0" format="html">
<text><![CDATA[ <p><strong>bolded text</strong></p> ]]></text>
<feedback format="html">
<text><![CDATA[ <p>Does this look like a verb? (bolded answer)</p> ]]></text>
</feedback>
</answer>
<answer fraction="100" format="html">
<text><![CDATA[ <p>To run</p> ]]></text>
<feedback format="html">
<text><![CDATA[ <p>This answer is correct</p> ]]></text>
</feedback>
</answer>
</question>
</quiz>
"""

def test_multichoice_question_parsing():
    """Verify that a Multichoice question is parsed correctly, checking all fields."""
    
    # Execute parsing using the parse_string function
    results = parse_string(MULTICHOICE_XML_CONTENT)
    
    # 2. Base ASSERTIONS
    
    multichoice_questions: List[MultiChoiceQuestion] = results.get('multichoice', [])
    assert len(multichoice_questions) == 1, "There should be exactly 1 Multichoice question."
    
    q: MultiChoiceQuestion = multichoice_questions[0]
    
    # 3. ASSERTIONS on Metadata and Feedback
    
    assert q.name == "Which of these is a verb?"
    assert q.type == "multichoice"
    assert q.text_pre_parse == "<p>Indicate which of the following words is a verb.</p>"
    
    # Verify specific Multichoice fields
    assert q.default_grade == 1.0
    assert q.penalty == 0.3333333
    assert q.single is True, "The <single> field should be True."
    assert q.shuffle_answers is True, "The <shuffleanswers> field should be True."
    assert q.answernumbering == "abc"
    
    # Verify feedback messages
    assert q.general_feedback.strip() == "<p>- test: general feedback -</p>"
    assert q.correct_feedback.strip() == "<p>Your answer is correct.</p>"
    assert q.incorrect_feedback.strip() == "<p>Your answer is incorrect.</p>"
    
    # 4. ASSERTIONS on Options
    
    assert len(q.options) == 2, "There should be exactly 2 answer options."
    
    # Option 1 (Incorrect)
    opt_wrong: Option = q.options[0]
    assert opt_wrong.answer == "<p><strong>bolded text</strong></p>"
    assert opt_wrong.score_fraction == 0
    assert "Does this look like a verb?" in opt_wrong.feedback
    
    # Option 2 (Correct)
    opt_correct: Option = q.options[1]
    assert opt_correct.answer == "<p>To run</p>"
    assert opt_correct.score_fraction == 100
    assert opt_correct.feedback == "<p>This answer is correct</p>"