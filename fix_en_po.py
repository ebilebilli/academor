# Fix the English translation file
with open('academor/locale/en/LC_MESSAGES/django.po', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the broken msgid around line 476-496
old_broken = '''#: academor/portals/admin/admin_v1.py:587
msgid ""
"Each part belongs to a speaking quiz. Select an existing speaking quiz, or "
"leave Quiz empty and enter a new topic and category — a speaking quiz will 

#: academor/templates/portals/includes/quiz_question_play.html
msgid "Answer format guidelines:"
msgstr "Answer format guidelines:"

#: academor/templates/portals/includes/quiz_question_play.html
msgid "Acceptable formats"
msgstr "Acceptable formats"

#: academor/templates/portals/includes/quiz_question_play.html
msgid "Unacceptable formats"
msgstr "Unacceptable formats"

#: academor/templates/portals/includes/quiz_question_play.html
msgid "Enter fractions as a/b (e.g., 7/2). Do not use mixed numbers or spaces. For decimals, include enough significant digits."
msgstr "Enter fractions as a/b (e.g., 7/2). Do not use mixed numbers or spaces. For decimals, include enough significant digits."
"be created automatically. Add speaking questions in the section below."
msgstr ""'''

new_fixed = '''#: academor/portals/admin/admin_v1.py:587
msgid ""
"Each part belongs to a speaking quiz. Select an existing speaking quiz, or "
"leave Quiz empty and enter a new topic and category — a speaking quiz will "
"be created automatically. Add speaking questions in the section below."
msgstr ""

#: academor/templates/portals/includes/quiz_question_play.html
msgid "Answer format guidelines:"
msgstr "Answer format guidelines:"

#: academor/templates/portals/includes/quiz_question_play.html
msgid "Acceptable formats"
msgstr "Acceptable formats"

#: academor/templates/portals/includes/quiz_question_play.html
msgid "Unacceptable formats"
msgstr "Unacceptable formats"

#: academor/templates/portals/includes/quiz_question_play.html
msgid "Enter fractions as a/b (e.g., 7/2). Do not use mixed numbers or spaces. For decimals, include enough significant digits."
msgstr "Enter fractions as a/b (e.g., 7/2). Do not use mixed numbers or spaces. For decimals, include enough significant digits."'''

content = content.replace(old_broken, new_fixed)

with open('academor/locale/en/LC_MESSAGES/django.po', 'w', encoding='utf-8') as f:
    f.write(content)

print("English translation file fixed!")