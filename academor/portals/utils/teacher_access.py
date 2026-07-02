"""Ownership checks — teachers may only manage their own portal data."""

from portals.models import Lesson, Quiz, QuizQuestion, Schedule
from portals.utils.student_courses import quiz_visible_to_teacher
from portals.utils.teacher_courses import teacher_groups_queryset


def teacher_groups_qs(teacher_id):
    return teacher_groups_queryset(teacher_id, active_only=False)


def get_teacher_group(teacher_id, group_id):
    return teacher_groups_qs(teacher_id).filter(pk=group_id).first()


def get_teacher_schedule(teacher_id, schedule_id):
    return Schedule.objects.filter(
        pk=schedule_id,
        group__teacher_id=teacher_id,
        group__in=teacher_groups_qs(teacher_id),
    ).first()


def get_teacher_lesson(teacher_id, lesson_id):
    return (
        Lesson.objects.filter(
            pk=lesson_id,
            teacher_id=teacher_id,
            group__teacher_id=teacher_id,
        )
        .select_related('group')
        .first()
    )


def get_teacher_quiz(teacher_id, quiz_id):
    quiz = (
        Quiz.objects.filter(pk=quiz_id)
        .select_related('category')
        .first()
    )
    if not quiz or not quiz_visible_to_teacher(quiz, teacher_id):
        return None
    return quiz


def get_teacher_quiz_question(teacher_id, quiz_id, question_id):
    quiz = get_teacher_quiz(teacher_id, quiz_id)
    if not quiz:
        return None
    return QuizQuestion.objects.filter(pk=question_id, quiz_id=quiz.pk).first()


def get_teacher_student(teacher_id, student_id):
    from portals.models import StudentProfile

    return (
        StudentProfile.objects.filter(
            pk=student_id,
            groups__in=teacher_groups_qs(teacher_id),
        )
        .distinct()
        .first()
    )
