"""Parse SAT Word documents and convert to JSON format for quiz loading."""
import json
import re
from pathlib import Path
from docx import Document

def extract_text_from_docx(docx_path):
    """Extract all text from a Word document."""
    doc = Document(docx_path)
    text = []
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            text.append(paragraph.text.strip())
    return '\n'.join(text)

def parse_sat_questions(text_content, answer_key_content=None):
    """Parse SAT questions from text content."""
    questions = []
    lines = text_content.split('\n')
    
    current_question = None
    question_number = 0
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Detect question start (e.g., "1.", "2.", "1)", "2)")
        question_match = re.match(r'^(\d+)[.\)]\s*(.*)', line)
        if question_match:
            # Save previous question if exists
            if current_question:
                questions.append(current_question)
            
            # Start new question
            question_number = int(question_match.group(1))
            current_question = {
                'id': question_number,
                'question': question_match.group(2),
                'options': [],
                'correct': None
            }
        elif current_question:
            # Check if this line is an answer option
            option_match = re.match(r'^([A-D])[.\)]\s*(.*)', line, re.IGNORECASE)
            if option_match:
                option_letter = option_match.group(1).upper()
                option_text = option_match.group(2)
                current_question['options'].append(option_text)
            else:
                # Append to question text
                if current_question['question']:
                    current_question['question'] += ' ' + line
                else:
                    current_question['question'] = line
    
    # Add last question
    if current_question:
        questions.append(current_question)
    
    # Parse answer key if provided
    if answer_key_content:
        answer_lines = answer_key_content.split('\n')
        answer_map = {}
        for line in answer_lines:
            line = line.strip()
            # Match patterns like "1. A", "1)A", "1-A", etc.
            answer_match = re.match(r'^(\d+)[.\)\-]\s*([A-D])', line, re.IGNORECASE)
            if answer_match:
                q_num = int(answer_match.group(1))
                answer = answer_match.group(2).upper()
                answer_map[q_num] = answer
        
        # Map answers to questions
        for q in questions:
            if q['id'] in answer_map:
                answer_letter = answer_map[q['id']]
                # Convert letter to index (A=0, B=1, C=2, D=3)
                answer_index = ord(answer_letter) - ord('A')
                if 0 <= answer_index < len(q['options']):
                    q['correct'] = q['options'][answer_index]
    
    return questions

def main():
    base_path = Path(r'c:\Users\user\Desktop\SAT Mock\One')
    
    # Read SAT Math One
    math_doc = base_path / 'SAT_Math_One.docx'
    math_answers = base_path / 'SAT_Math_One_Answer_Keys.docx'
    
    print(f"Reading {math_doc}...")
    math_text = extract_text_from_docx(math_doc)
    print(f"Reading {math_answers}...")
    math_answers_text = extract_text_from_docx(math_answers)
    
    math_questions = parse_sat_questions(math_text, math_answers_text)
    print(f"Parsed {len(math_questions)} Math questions")
    
    # Create JSON for Math
    math_json = {
        'title': 'SAT Math One',
        'category_name': 'SAT Math',
        'service': 'sat',
        'is_sat': True,
        'sat_section': 'algebra',  # Will need to determine actual section
        'questions': math_questions
    }
    
    output_path = Path('c:\\Users\\user\\Desktop\\Academor\\academor\\portals\\resources\\quiz_questions\\sat_math_one.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(math_json, f, indent=2, ensure_ascii=False)
    print(f"Saved Math questions to {output_path}")
    
    # Read SAT Verbal One
    verbal_doc = base_path / 'SAT_Verbal_One.docx'
    verbal_answers = base_path / 'Sat_Verbal_One_Answer_Keys.docx'
    
    print(f"\nReading {verbal_doc}...")
    verbal_text = extract_text_from_docx(verbal_doc)
    print(f"Reading {verbal_answers}...")
    verbal_answers_text = extract_text_from_docx(verbal_answers)
    
    verbal_questions = parse_sat_questions(verbal_text, verbal_answers_text)
    print(f"Parsed {len(verbal_questions)} Verbal questions")
    
    # Create JSON for Verbal
    verbal_json = {
        'title': 'SAT Verbal One',
        'category_name': 'SAT Verbal',
        'service': 'sat',
        'is_sat': True,
        'sat_section': 'reading',  # Will need to determine actual section
        'questions': verbal_questions
    }
    
    output_path = Path('c:\\Users\\user\\Desktop\\Academor\\academor\\portals\\resources\\quiz_questions\\sat_verbal_one.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(verbal_json, f, indent=2, ensure_ascii=False)
    print(f"Saved Verbal questions to {output_path}")
    
    # Print sample questions for review
    print("\n=== Sample Math Questions ===")
    for q in math_questions[:3]:
        try:
            print(f"\nQuestion {q['id']}: {q['question'][:100]}...")
        except UnicodeEncodeError:
            print(f"\nQuestion {q['id']}: [Unicode text]")
        print(f"Options: {q['options']}")
        print(f"Correct: {q['correct']}")
    
    print("\n=== Sample Verbal Questions ===")
    for q in verbal_questions[:3]:
        try:
            print(f"\nQuestion {q['id']}: {q['question'][:100]}...")
        except UnicodeEncodeError:
            print(f"\nQuestion {q['id']}: [Unicode text]")
        print(f"Options: {q['options']}")
        print(f"Correct: {q['correct']}")

if __name__ == '__main__':
    main()
