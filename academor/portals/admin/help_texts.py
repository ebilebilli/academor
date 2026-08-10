"""
Help copy for the student/parent/teacher portal admin (translatable).
"""

from django.utils.translation import gettext_lazy as _


ADMIN_HELP = {
    'TeacherProfile': {
        'icon': 'T',
        'title': _('Teachers'),
        'summary': _(
            'Create teacher login profiles. Teachers mark attendance, upload lessons, '
            'enter scores, and manage quizzes in the private portal.'
        ),
        'where': _('Private teacher portal — not visible on academor.az.'),
        'workflow': [
            {'title': _('Add user'), 'text': _('Authentication → Users → Add user (role, username, optional phone in one form)')},
            {'title': _('Add teacher profile'), 'text': _('Or use Users form with role Teacher — profile is created automatically')},
            {'title': _('Assign courses'), 'text': _('Add one or more course specializations below')},
            {'title': _('Assign a group'), 'text': _('Study groups → pick this teacher and matching course type')},
        ],
        'tips': [
            _('One user = one teacher profile only.'),
            _('Teachers only see lessons, quizzes, and groups for their assigned courses.'),
        ],
    },
    'StudentProfile': {
        'icon': 'S',
        'title': _('Students'),
        'summary': _(
            'Student accounts: username, optional phone, and login. '
            'Assign active service enrollments on this page — quizzes and classrooms '
            'follow those services. Groups are for schedule and attendance only.'
        ),
        'where': _('Private student portal — not on the public website.'),
        'workflow': [
            {'title': _('Add user'), 'text': _('Authentication → Users → Add user (role Student, username, optional phone)')},
            {'title': _('Assign services'), 'text': _('Add one or more active service enrollments below')},
            {'title': _('Assign groups'), 'text': _('Study groups → pick this student for schedule')},
        ],
        'tips': [
            _('A student can be enrolled in several services (e.g. IELTS + Speaking) and see quizzes for all of them.'),
            _('Service enrollments are assigned only on this page — not copied from study groups.'),
            _('Deactivate a service enrollment instead of deleting it to pause access.'),
            _('Without any active service, the student will not see quizzes or classrooms.'),
            _('Phone example: +994501234567 or 0501234567.'),
        ],
    },
    'ParentProfile': {
        'icon': 'P',
        'title': _('Parents'),
        'summary': _(
            'Parent accounts linked to one or more students. Parents view attendance, '
            'scores, and quiz results for linked children only — quiz visibility follows '
            'each child\'s active service enrollments.'
        ),
        'where': _('Private parent portal — not on the public website.'),
        'workflow': [
            {'title': _('Add user'), 'text': _('Authentication → Users → role Parent, username, optional phone, linked students')},
            {'title': _('Save'), 'text': _('Parent can log in immediately')},
        ],
        'tips': [
            _('Select every child this parent should see in the portal.'),
            _('One parent account can be linked to several students.'),
            _('Phone is optional but useful for contact.'),
        ],
    },
    'CustomerProfile': {
        'icon': 'C',
        'title': _('Customers'),
        'summary': _(
            'Paid mock-test portal users. Each customer has mock credits; '
            'one credit is used per mock test start. Credits can be set manually '
            'or added automatically after a successful package payment.'
        ),
        'where': _('Private customer portal — mock test and package purchase only.'),
        'workflow': [
            {'title': _('Add user'), 'text': _('Authentication → Users → role Customer, username, reviewing teacher, optional phone, initial mock credits')},
            {'title': _('Packages'), 'text': _('Mock test packages → define credit bundles and prices for United Payment checkout')},
            {'title': _('Adjust credits'), 'text': _('Edit mock credits here after offline payment or support requests')},
        ],
        'tips': [
            _('Assign a reviewing teacher so Writing and Speaking mock submissions appear in that teacher\'s review queue.'),
            _('Customers do not see lessons, quizzes, or schedule — only mock test pages.'),
            _('Set initial mock credits when creating the account for customers who already paid offline.'),
        ],
    },
    'StudyGroup': {
        'icon': 'G',
        'title': _('Study groups'),
        'summary': _(
            'A class: linked courses, teacher, capacity, and enrolled students. '
            'Use the Students box to add or remove members.'
        ),
        'where': _('Portal — lessons, schedule, and videos for this group.'),
        'workflow': [
            {'title': _('Create group'), 'text': _('Name, courses, and teacher')},
            {'title': _('Add students'), 'text': _('Select members in the Students field')},
            {'title': _('Add schedule'), 'text': _('Weekly slots in the table below')},
        ],
        'tips': [
            _('Students field: pick one or many — same student can be in multiple groups.'),
            _('Max students shows as a capacity bar in the list.'),
            _('Turn off Active to hide without deleting history.'),
        ],
    },
    'Schedule': {
        'icon': '⏰',
        'title': _('Weekly schedule'),
        'summary': _('Recurring class times: weekday, start, duration, room or online link.'),
        'where': _('Portal schedule for students, parents, and teachers.'),
        'workflow': [
            {'title': _('Pick group'), 'text': _('Which class this slot belongs to')},
            {'title': _('Set day & time'), 'text': _('e.g. Monday 18:00, 90 min')},
            {'title': _('Active from'), 'text': _('First date the slot appears on the calendar')},
            {'title': _('Add room/link'), 'text': _('Classroom or Zoom URL')},
        ],
        'tips': [
            _('Slots are hidden in past weeks before Active from.'),
            _('When marking attendance, also enter the real session date.'),
        ],
    },
    'Lesson': {
        'icon': '📚',
        'title': _('Lessons & materials'),
        'summary': _('Upload PDFs, videos, and images for students in a group.'),
        'where': _('Portal lesson list for that group.'),
        'tips': [
            _('Teachers can type a new category when uploading, or reuse an existing one.'),
            _('Teacher should match the group leader when possible.'),
        ],
    },
    'LessonCategory': {
        'icon': '🏷',
        'title': _('Lesson categories'),
        'summary': _('Topics within a service (e.g. Grammar, Homework) for organizing lesson materials.'),
        'where': _('Teacher lesson upload form and future category tabs.'),
        'tips': [
            _('One category name per service — e.g. IELTS → Writing.'),
        ],
    },
    'VideoRecord': {
        'icon': '▶',
        'title': _('Recorded videos'),
        'summary': _('YouTube recordings of past classes for a group.'),
        'where': _('Portal video archive.'),
        'tips': [
            _('Paste the full YouTube URL.'),
            _('Lesson date helps students browse by week.'),
        ],
    },
    'Attendance': {
        'icon': '✓',
        'title': _('Attendance'),
        'summary': _('Mark present, absent, or late for a specific class date.'),
        'where': _('Teachers mark; students and parents can view.'),
        'workflow': [
            {'title': _('Pick schedule slot'), 'text': _('The weekly time slot')},
            {'title': _('Pick session date'), 'text': _('Real calendar date, e.g. 15.03.2026')},
            {'title': _('Mark status'), 'text': _('Present / Absent / Late')},
        ],
        'tips': [
            _('Session date is required — it is not the weekday alone.'),
            _('Add a note for excused absences if needed.'),
        ],
    },
    'Score': {
        'icon': '★',
        'title': _('Grades & scores'),
        'summary': _('Homework, exam, or quiz results with score and feedback.'),
        'where': _('Visible to student, parents, and teachers.'),
        'tips': [
            _('Max value is often 100 for percentage-style grades.'),
            _('Lesson link is optional.'),
        ],
    },
    'WeeklyStudentScore': {
        'icon': 'W',
        'title': _('Weekly scores'),
        'summary': _('Teacher weekly score out of 10 for each student.'),
        'where': _('Teachers enter from portal; students view their history.'),
        'tips': [
            _('Week start must be Monday.'),
            _('One score per teacher, student, and week.'),
        ],
    },
    'QuizCategory': {
        'icon': 'C',
        'title': _('Quiz categories'),
        'summary': _(
            'Named categories under a service. Quizzes link here; '
            'students and teachers reach services indirectly through category.'
        ),
        'where': _('Admin taxonomy for quiz organization.'),
        'workflow': [
            {'title': _('Pick service tab'), 'text': _('Filter categories by service')},
            {'title': _('Create category'), 'text': _('Service + name, e.g. IELTS → Reading practice')},
            {'title': _('Assign to quiz'), 'text': _('Open Quiz and pick this category')},
        ],
        'tips': [
            _('Same service + name must be unique.'),
            _('Service must match an active site service.'),
            _('Drag rows on the category list to set portal tab order (filter by service first).'),
        ],
    },
    'Quiz': {
        'icon': '?',
        'title': _('Quizzes'),
        'summary': _('Quiz sets with prompts for students. Created and managed here in admin only.'),
        'where': _('Portal quiz section (read-only preview for teachers).'),
        'workflow': [
            {'title': _('Create category'), 'text': _('Quiz categories → service + name')},
            {'title': _('Create quiz'), 'text': _('Teacher, category, topic, grading mode')},
            {'title': _('Add questions'), 'text': _('Use the inline table below')},
        ],
        'tips': [
            _('Variant quiz: answer options = JSON list ["A", "B", "C", "D"]'),
            _('Listening / Essay / Speaking: only one mode at a time — teacher reviews submissions manually.'),
            _('Manual quizzes have no multiple-choice variants.'),
        ],
        'json_example': '["Option A", "Option B", "Option C", "Option D"]',
    },
    'QuizQuestion': {
        'icon': '?',
        'title': _('Quiz questions'),
        'summary': _('One question with text, image, video, or audio and JSON answer choices.'),
        'where': _('Shown during the quiz.'),
        'tips': [
            _('Lower order number = shown first.'),
            _('Correct answer must exactly match one option string.'),
            _('For image / video / audio, upload a file or paste a media URL.'),
            _('Question type switches the form instantly — no page reload needed.'),
        ],
        'json_example': '["True", "False"]',
    },
    'QuizResult': {
        'icon': '📊',
        'title': _('Quiz results'),
        'summary': _('Student attempts — auto-scored for variant quizzes, teacher-reviewed for Listening / Essay / Speaking.'),
        'where': _('Read-only history for staff; manual quizzes need teacher feedback and score.'),
        'tips': [
            _('Variant quizzes: scored automatically from given answers.'),
            _('Manual quizzes (Listening / Essay / Speaking): score from 0 to 10, plus teacher feedback.'),
            _('Filter by student or quiz to find attempts.'),
        ],
    },
    'Classroom': {
        'icon': '📖',
        'title': _('Textbooks'),
        'summary': _('Group textbook PDFs created by teachers for their students.'),
        'where': _('Portal Textbooks page — visible to students in the matching group.'),
        'tips': [
            _('Pick active site services with the multi-select box (service slug is the key).'),
            _('Only users with a matching active service enrollment see the room.'),
        ],
    },
}


def get_admin_help(model):
    """Return help dict for a portal model class, or None."""
    return ADMIN_HELP.get(model.__name__)
