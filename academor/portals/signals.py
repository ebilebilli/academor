"""
Portal ORM signals: profile image resize + cache invalidation.

Keep in sync with portals.utils.queries @cached_query / @cached_page_data readers.
"""
from django.core.signals import request_finished, request_started
from django.db import transaction
from django.db.models.signals import m2m_changed, post_delete, post_save, pre_save
from django.dispatch import receiver

from portals.models import (
    Attendance,
    Classroom,
    IeltsMockTestAttempt,
    Lesson,
    LessonAttachment,
    LessonCategory,
    ListeningAudio,
    ListeningQuestion,
    ReadingPassage,
    ReadingQuestion,
    ReadingQuestionGroup,
    SpeakingPart,
    SpeakingQuestion,
    SpeakingRecording,
    ParentProfile,
    CustomerProfile,
    PortalNotification,
    Quiz,
    QuizAssignment,
    QuizCategory,
    QuizQuestion,
    QuizResult,
    QuizResultReview,
    Schedule,
    Score,
    WeeklyStudentScore,
    StudentCourseSpecialization,
    StudentMockAccess,
    StudentProfile,
    StudyGroup,
    TeacherProfile,
    TeacherCourseSpecialization,
    VideoRecord,
)
from portals.utils.admin_access import strip_admin_flags_for_portal_user
from portals.utils.cache_utils import invalidate_model_cache
from portals.utils.image_resize import resize_image_field
from portals.utils.portal_services import reset_active_service_snapshot
from projects.models.service_models import Service

PROFILE_IMAGE_MAX_PX = 400
LESSON_IMAGE_MAX_WIDTH = 1920
LESSON_IMAGE_MAX_HEIGHT = 1080


def _compress_image_field(instance, field_name, *, max_width, max_height):
    field_file = getattr(instance, field_name, None)
    if not field_file or not _image_field_changed(instance, field_name):
        return
    resize_image_field(
        field_file,
        max_width=max_width,
        max_height=max_height,
    )


# NOTE: With separate cookies (portal_sessionid vs sessionid), admin login
# does NOT affect portal session anymore. No signal needed.


def _invalidate_on_commit(model_name):
    transaction.on_commit(lambda: invalidate_model_cache(model_name))


def _image_field_changed(instance, field_name):
    if not instance.pk:
        return True
    try:
        old = instance.__class__.objects.only(field_name).get(pk=instance.pk)
    except instance.__class__.DoesNotExist:
        return True
    old_file = getattr(old, field_name)
    new_file = getattr(instance, field_name)
    return (old_file or '') != (new_file or '')


def _register_model_cache(model):
    name = model.__name__

    @receiver(post_save, sender=model)
    @receiver(post_delete, sender=model)
    def _invalidate(sender, instance, **kwargs):
        _invalidate_on_commit(name)


for _model in (
    TeacherProfile,
    TeacherCourseSpecialization,
    StudentProfile,
    StudentCourseSpecialization,
    ParentProfile,
    StudyGroup,
    Schedule,
    Lesson,
    LessonCategory,
    Classroom,
    VideoRecord,
    Attendance,
    Score,
    WeeklyStudentScore,
    QuizCategory,
    Quiz,
    QuizAssignment,
    QuizQuestion,
    QuizResult,
    PortalNotification,
    ListeningAudio,
    ListeningQuestion,
    ReadingPassage,
    ReadingQuestion,
    ReadingQuestionGroup,
    IeltsMockTestAttempt,
    StudentMockAccess,
    SpeakingRecording,
):
    _register_model_cache(_model)


for _review_model in (QuizResultReview,):
    _register_model_cache(_review_model)


@receiver(m2m_changed, sender=Classroom.services.through)
def invalidate_classroom_services_m2m(sender, instance, action, **kwargs):
    if action in ('post_add', 'post_remove', 'post_clear'):
        _invalidate_on_commit('Classroom')


@receiver(m2m_changed, sender=ParentProfile.students.through)
def invalidate_parent_students_m2m(sender, instance, action, **kwargs):
    if action in ('post_add', 'post_remove', 'post_clear'):
        _invalidate_on_commit('ParentProfile')
        _invalidate_on_commit('StudentProfile')
        _invalidate_on_commit('Quiz')
        _invalidate_on_commit('QuizResult')
        _invalidate_on_commit('Classroom')


@receiver(m2m_changed, sender=StudyGroup.students.through)
def enforce_study_group_max_students(sender, instance, action, pk_set, **kwargs):
    if action != 'pre_add' or not pk_set:
        return
    from django.core.exceptions import ValidationError
    from django.utils.translation import gettext as _

    limit = instance.max_students or 0
    if limit <= 0:
        return
    current = instance.students.count()
    new_ids = set(pk_set) - set(instance.students.values_list('pk', flat=True))
    if current + len(new_ids) > limit:
        raise ValidationError(
            _('This group allows at most %(limit)s students (%(current)s already enrolled).')
            % {'limit': limit, 'current': current},
        )


@receiver(m2m_changed, sender=StudyGroup.students.through)
def sync_student_group_course_enrollments(sender, instance, action, pk_set, **kwargs):
    if action != 'post_add' or not pk_set:
        return
    from portals.utils.student_courses import ensure_student_group_course_enrollments

    for student_id in pk_set:
        if student_id:
            ensure_student_group_course_enrollments(student_id, instance)
    _invalidate_on_commit('StudentCourseSpecialization')


@receiver(m2m_changed, sender=StudyGroup.students.through)
def invalidate_study_group_students_m2m(sender, instance, action, **kwargs):
    if action in ('post_add', 'post_remove', 'post_clear'):
        _invalidate_on_commit('StudyGroup')
        _invalidate_on_commit('StudentProfile')
        _invalidate_on_commit('Quiz')
        _invalidate_on_commit('QuizResult')
        _invalidate_on_commit('Classroom')


@receiver(post_save, sender=TeacherCourseSpecialization)
@receiver(post_delete, sender=TeacherCourseSpecialization)
def sync_teacher_course_specialization_text(sender, instance, **kwargs):
    from portals.utils.teacher_courses import sync_teacher_specialization_text

    if instance.teacher_id:
        sync_teacher_specialization_text(instance.teacher_id)
    _invalidate_on_commit('Quiz')
    _invalidate_on_commit('Classroom')


@receiver(post_save, sender=ListeningAudio)
@receiver(post_delete, sender=ListeningAudio)
@receiver(post_save, sender=ListeningQuestion)
@receiver(post_delete, sender=ListeningQuestion)
def invalidate_quiz_on_listening_content_change(sender, instance, **kwargs):
    _invalidate_on_commit('ListeningAudio')
    _invalidate_on_commit('ListeningQuestion')
    _invalidate_on_commit('Quiz')
    _invalidate_on_commit('QuizResult')


@receiver(post_save, sender=ReadingPassage)
@receiver(post_delete, sender=ReadingPassage)
@receiver(post_save, sender=ReadingQuestion)
@receiver(post_delete, sender=ReadingQuestion)
@receiver(post_save, sender=ReadingQuestionGroup)
@receiver(post_delete, sender=ReadingQuestionGroup)
def invalidate_quiz_on_reading_content_change(sender, instance, **kwargs):
    _invalidate_on_commit('ReadingPassage')
    _invalidate_on_commit('ReadingQuestion')
    _invalidate_on_commit('ReadingQuestionGroup')
    _invalidate_on_commit('Quiz')
    _invalidate_on_commit('QuizResult')


@receiver(post_save, sender=SpeakingPart)
@receiver(post_delete, sender=SpeakingPart)
@receiver(post_save, sender=SpeakingQuestion)
@receiver(post_delete, sender=SpeakingQuestion)
def invalidate_quiz_on_speaking_content_change(sender, instance, **kwargs):
    _invalidate_on_commit('SpeakingPart')
    _invalidate_on_commit('SpeakingQuestion')
    _invalidate_on_commit('Quiz')
    _invalidate_on_commit('QuizResult')


@receiver(post_save, sender=QuizCategory)
@receiver(post_delete, sender=QuizCategory)
def invalidate_quiz_on_category_change(sender, instance, **kwargs):
    _invalidate_on_commit('QuizCategory')
    _invalidate_on_commit('Quiz')
    _invalidate_on_commit('QuizResult')


@receiver(post_save, sender=TeacherProfile)
@receiver(post_save, sender=StudentProfile)
@receiver(post_save, sender=ParentProfile)
@receiver(post_save, sender=CustomerProfile)
def portal_profile_strip_admin_flags(sender, instance, **kwargs):
    if instance.user_id:
        strip_admin_flags_for_portal_user(instance.user)


@receiver(pre_save, sender=StudentProfile)
def resize_student_profile_image(sender, instance, **kwargs):
    _compress_image_field(
        instance,
        'profile_image',
        max_width=PROFILE_IMAGE_MAX_PX,
        max_height=PROFILE_IMAGE_MAX_PX,
    )


@receiver(pre_save, sender=TeacherProfile)
def resize_teacher_profile_image(sender, instance, **kwargs):
    _compress_image_field(
        instance,
        'profile_image',
        max_width=PROFILE_IMAGE_MAX_PX,
        max_height=PROFILE_IMAGE_MAX_PX,
    )


@receiver(pre_save, sender=Lesson)
def resize_lesson_image(sender, instance, **kwargs):
    _compress_image_field(
        instance,
        'image',
        max_width=LESSON_IMAGE_MAX_WIDTH,
        max_height=LESSON_IMAGE_MAX_HEIGHT,
    )


@receiver(pre_save, sender=LessonAttachment)
def resize_lesson_attachment_image(sender, instance, **kwargs):
    if instance.kind != LessonAttachment.Kind.IMAGE or not instance.file:
        return
    _compress_image_field(
        instance,
        'file',
        max_width=LESSON_IMAGE_MAX_WIDTH,
        max_height=LESSON_IMAGE_MAX_HEIGHT,
    )


@receiver(post_save, sender=LessonAttachment)
@receiver(post_delete, sender=LessonAttachment)
def invalidate_lesson_on_attachment_change(sender, instance, **kwargs):
    _invalidate_on_commit('Lesson')


# portal_services memoizes the active-service lookups for the duration of a
# single request; drop it at both request boundaries and whenever a Service
# row changes so no request ever reads a stale course/service mapping.
request_started.connect(reset_active_service_snapshot, dispatch_uid='portals_service_snapshot_start')
request_finished.connect(reset_active_service_snapshot, dispatch_uid='portals_service_snapshot_end')


@receiver(post_save, sender=Service)
@receiver(post_delete, sender=Service)
def reset_service_snapshot_on_change(sender, instance, **kwargs):
    reset_active_service_snapshot()
    _invalidate_on_commit('Service')
