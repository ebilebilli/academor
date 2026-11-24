"""Public SAT / IELTS level tests that run portal quizzes (see projects/utils/level_exam.py).

intro (name + phone) -> section 1..n with the portal exam screen -> result.
"""

import json
import logging

from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.templatetags.static import static
from django.utils.translation import gettext as _
from django.views import View
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator

from projects.forms.forms_v1 import TestUserForm
from projects.models import Test, UserResult
from projects.utils import level_exam as lx
from projects.utils.queries import (
    get_language_from_request,
    localized_test_description,
    localized_test_title,
)

logger = logging.getLogger('projects.level_exam')

SAT_DISCOUNT_PERCENT = 50
SAT_DISCOUNT_MONTHS = 2
IELTS_DISCOUNT_PERCENT = 25
# illustration drawn on the shared result image and shown on the intro page
STORY_ART = 'assets/img/level-test/compass-notes.webp'


def get_exam_test(test_id: int):
    """Active test that runs portal quizzes, or None (fresh, not cached: M2M edits show at once)."""
    test = (
        Test.objects.filter(pk=test_id, is_active=True)
        .prefetch_related('portal_quizzes__category')
        .first()
    )
    if not test or not lx.exam_quizzes(test):
        return None
    return test


def is_exam_test(test_id: int) -> bool:
    return Test.objects.filter(pk=test_id, is_active=True, portal_quizzes__isnull=False).exists()


def _exam_context(request, test):
    lang = get_language_from_request(request)
    quizzes = lx.exam_quizzes(test)
    kind = lx.exam_kind(quizzes)
    sections = []
    for index, quiz in enumerate(quizzes, start=1):
        sections.append({
            'index': index,
            'quiz': quiz,
            'label': lx.section_label(quiz),
            'kind': lx.section_kind(quiz),
            'minutes': lx.section_minutes(quiz),
            'question_count': lx.question_count(quiz),
        })
    return {
        'exam_test': test,
        'exam_title': localized_test_title(test, lang),
        'exam_description': localized_test_description(test, lang),
        'exam_kind': kind,
        'exam_sections': sections,
        'exam_total_minutes': sum(s['minutes'] or 0 for s in sections),
        'exam_total_questions': sum(s['question_count'] for s in sections),
        'is_sat': kind == lx.KIND_SAT,
        'is_listening': kind == lx.KIND_IELTS_LISTENING,
        'is_ielts': kind in (lx.KIND_IELTS_READING, lx.KIND_IELTS_LISTENING),
        'ielts_discount_percent': IELTS_DISCOUNT_PERCENT,
        'sat_discount_percent': SAT_DISCOUNT_PERCENT,
        'sat_discount_months': SAT_DISCOUNT_MONTHS,
        'language': lang,
    }


def exam_test_cards(tests, lang):
    """Cards for the tests page: SAT / IELTS exams built from portal quizzes (classic tests skipped)."""
    from django.db.models import Prefetch

    from portals.models import Quiz, QuizQuestion

    ids = [t.pk for t in tests]
    rows = (
        Test.objects.filter(pk__in=ids, portal_quizzes__isnull=False)
        .distinct()
        .prefetch_related(
            Prefetch(
                'portal_quizzes',
                queryset=Quiz.objects.prefetch_related(
                    Prefetch('questions', queryset=QuizQuestion.objects.order_by('order', 'id')),
                ),
            ),
        )
    )
    cards = []
    for test in rows:
        quizzes = lx.exam_quizzes(test)
        if not quizzes:
            continue
        kind = lx.exam_kind(quizzes)
        cards.append({
            'id': test.pk,
            'title': localized_test_title(test, lang),
            'description': localized_test_description(test, lang),
            'kind': kind,
            'sections': [str(lx.section_label(q)) for q in quizzes],
            'question_count': sum(lx.question_count(q) for q in quizzes),
            'minutes': sum(lx.section_minutes(q) or 0 for q in quizzes),
        })
    return cards


def _section_url(test_id, index):
    return reverse('projects:level-exam-section', kwargs={'test_id': test_id, 'section': index})


def _result_url(test_id):
    return reverse('projects:level-exam-result', kwargs={'test_id': test_id})


def _attempt_result(attempt):
    if not attempt:
        return None
    return UserResult.objects.filter(pk=attempt['result_id']).first()


def _next_url(test_id, attempt, total_sections):
    done = int(attempt.get('done', 0))
    if done >= total_sections:
        return _result_url(test_id)
    return _section_url(test_id, done + 1)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class LevelExamIntroView(View):
    """Test landing: what to expect, the SAT offer, and the name / phone form."""

    template_name = 'level-exam-intro.html'

    def _render(self, request, test, form, status=200):
        ctx = _exam_context(request, test)
        attempt = lx.get_attempt(request, test.pk)
        total = len(ctx['exam_sections'])
        ctx.update({
            'user_form': form,
            'resume_url': _next_url(test.pk, attempt, total) if attempt else '',
            'page_title': f"{ctx['exam_title']} | Academor",
            'page_description': (ctx['exam_description'] or ctx['exam_title'])[:320],
        })
        return render(request, self.template_name, ctx, status=status)

    def get(self, request, test_id):
        test = get_exam_test(test_id)
        if not test:
            raise Http404(_('Test not found'))
        return self._render(request, test, TestUserForm())

    def post(self, request, test_id):
        test = get_exam_test(test_id)
        if not test:
            raise Http404(_('Test not found'))
        form = TestUserForm(request.POST)
        if not form.is_valid():
            return self._render(request, test, form, status=200)
        data = form.cleaned_data
        quizzes = lx.exam_quizzes(test)
        kind = lx.exam_kind(quizzes)
        now = timezone.now()
        result = UserResult.objects.create(
            first_name=data['first_name'],
            last_name=data.get('last_name') or '',
            number=data['number'],
            email=data.get('email') or None,
            test=test,
            score=0,
            level='Başladı',
            details={
                'kind': kind,
                'status': 'started',
                'started_at': now.isoformat(),
                'sections': [],
            },
        )
        lx.save_attempt(request, test.pk, {'result_id': result.pk, 'done': 0, 'started': {}})
        return redirect(_section_url(test.pk, 1))


@method_decorator(ensure_csrf_cookie, name='dispatch')
class LevelExamSectionView(View):
    """One section on the portal exam screen, inside the focused exam layout."""

    def get(self, request, test_id, section):
        test = get_exam_test(test_id)
        if not test:
            raise Http404(_('Test not found'))
        attempt = lx.get_attempt(request, test.pk)
        if not attempt or not _attempt_result(attempt):
            return redirect('projects:test-take', test_id=test.pk)
        quizzes = lx.exam_quizzes(test)
        expected = int(attempt.get('done', 0)) + 1
        if section != expected:
            return redirect(_next_url(test.pk, attempt, len(quizzes)))

        quiz = lx._load_quiz(quizzes[section - 1].pk)
        payload = lx.build_take_payload(quiz) if quiz else None
        if not payload:
            logger.warning('Level exam section has no questions test=%s quiz=%s', test.pk, getattr(quiz, 'pk', None))
            raise Http404(_('Test not found'))

        ctx = _exam_context(request, test)
        kwargs = {'test_id': test.pk, 'section': section}
        ctx.update({
            'quiz_base_template': 'level-exam-base.html',
            'quiz': payload,
            'submit_url': reverse('projects:level-exam-submit', kwargs=kwargs),
            'start_url': reverse('projects:level-exam-start', kwargs=kwargs),
            'back_url': reverse('projects:tests-page'),
            'quiz_cancel_url': reverse('projects:tests-page'),
            'exam_section_index': section,
            'exam_section_total': len(quizzes),
            'exam_section_label': lx.section_label(quiz),
        })
        return render(request, lx.TAKE_TEMPLATES[lx.section_format(quiz)], ctx)


def _json_body(request):
    try:
        data = json.loads(request.body or b'{}')
    except (TypeError, ValueError):
        return None
    return data if isinstance(data, dict) else None


class LevelExamStartView(View):
    """Start gate: remember when the section began (kept on reload, so the clock is fair)."""

    def post(self, request, test_id, section):
        test = get_exam_test(test_id)
        attempt = lx.get_attempt(request, test_id) if test else None
        if not test or not attempt or section != int(attempt.get('done', 0)) + 1:
            return JsonResponse({'success': False, 'redirect_url': reverse('projects:test-take', kwargs={'test_id': test_id})})
        started = dict(attempt.get('started') or {})
        started.setdefault(str(section), timezone.now().isoformat())
        attempt['started'] = started
        lx.save_attempt(request, test_id, attempt)
        return JsonResponse({'success': True})


class LevelExamSubmitView(View):
    """Score the section with the portal scorer, store it, and move on (no answer key is sent)."""

    def post(self, request, test_id, section):
        test = get_exam_test(test_id)
        attempt = lx.get_attempt(request, test_id) if test else None
        result = _attempt_result(attempt)
        if not test or not attempt or not result:
            return JsonResponse({'success': False, 'redirect_url': reverse('projects:test-take', kwargs={'test_id': test_id})})
        quizzes = lx.exam_quizzes(test)
        if section != int(attempt.get('done', 0)) + 1:
            # already submitted (double click, leave + timer): just continue
            return JsonResponse({'success': True, 'mock_continue': True, 'next_url': _next_url(test_id, attempt, len(quizzes))})
        data = _json_body(request)
        if data is None:
            return JsonResponse({'success': False, 'error': _('Could not submit the test. Please try again.')}, status=400)

        quiz = lx._load_quiz(quizzes[section - 1].pk)
        started_at = (attempt.get('started') or {}).get(str(section))
        scored = lx.score_section(quiz, data)
        kind = lx.exam_kind(quizzes)
        band = lx.ielts_band(kind, scored['correct'], scored['total'])
        elapsed = lx.elapsed_seconds(started_at)
        minutes = lx.section_minutes(quiz)
        duration = elapsed if elapsed is not None else 0
        if minutes:
            duration = min(duration, minutes * 60)
        trigger = str(data.get('completion_trigger') or 'manual')
        row = {
            'quiz_id': quiz.pk,
            'label': str(lx.section_label(quiz)),
            'kind': lx.section_kind(quiz),
            'correct': scored['correct'],
            'total': scored['total'],
            'band': band,
            'band_label': lx.format_band(band),
            'wrong': scored['wrong'],
            'unanswered': scored['unanswered'],
            'answers': scored['answers'],
            'duration_sec': duration,
            'trigger': trigger if trigger in ('manual', 'time_limit', 'auto_leave') else 'manual',
            'late': lx.section_was_late(quiz, started_at),
        }

        details = dict(result.details or {})
        sections = [s for s in details.get('sections') or [] if s.get('quiz_id') != quiz.pk]
        sections.append(row)
        details['sections'] = sections
        finished = section >= len(quizzes)
        if finished:
            details['status'] = 'finished'
            details['finished_at'] = timezone.now().isoformat()
        result.details = details
        result.score = sum(s['correct'] for s in sections)
        result.level = lx.summary_level(kind, sections) if finished else 'Davam edir'
        result.save(update_fields=['details', 'score', 'level'])
        if finished:
            _notify_crm(result)

        attempt['done'] = section
        lx.save_attempt(request, test_id, attempt)
        next_url = _next_url(test_id, attempt, len(quizzes))
        if trigger == 'auto_leave':
            # visitor clicked away mid-section: answers are saved, let them go where they wanted
            return JsonResponse({'success': True, 'questions': [], 'breakdown': [], 'total_score': 0, 'max_score': 0, 'percent': 0})
        return JsonResponse({'success': True, 'mock_continue': True, 'next_url': next_url})


def _notify_crm(result):
    try:
        from portals.utils.crm_leads import level_exam_finished

        level_exam_finished(result)
    except Exception:  # the CRM must never break the visitor's result
        logger.exception('CRM update failed for level exam result=%s', result.pk)


class LevelExamResultView(View):
    template_name = 'level-exam-result.html'

    def get(self, request, test_id):
        test = get_exam_test(test_id)
        if not test:
            raise Http404(_('Test not found'))
        attempt = lx.get_attempt(request, test_id)
        result = _attempt_result(attempt)
        if not result:
            return redirect('projects:test-take', test_id=test_id)
        details = result.details or {}
        ctx = _exam_context(request, test)
        if details.get('status') != 'finished':
            return redirect(_next_url(test_id, attempt, len(ctx['exam_sections'])))

        rows = []
        for row in details.get('sections') or []:
            pct = lx.percent(row.get('correct', 0), row.get('total', 0))
            band = row.get('band')
            if band is not None:
                scale = {'scale_pct': f'{band / 9 * 100:.1f}', 'marker': row.get('band_label'), 'ticks': list(range(0, 10))}
            else:
                scale = {'scale_pct': str(pct), 'marker': f'{pct}%', 'ticks': [0, 25, 50, 75, 100]}
            rows.append({**row, 'percent': pct, **scale})
        sat_scaled = lx.sat_scaled_scores(test, rows) if ctx['is_sat'] else None
        if sat_scaled:
            for row in rows:
                found = sat_scaled['sections'].get(row.get('quiz_id'))
                if found:
                    row['scaled'] = lx.format_score_range(found['low'], found['high'])
            if 'total_low' in sat_scaled:
                ctx['sat_total'] = lx.format_score_range(sat_scaled['total_low'], sat_scaled['total_high'])
        if ctx['is_sat']:
            whatsapp_text = _(
                'Hello! I took the SAT practice test on the Academor website (%(score)s). '
                'I would like to join SAT lessons with the %(percent)s%% discount for the first %(months)s months.'
            ) % {'score': result.level, 'percent': SAT_DISCOUNT_PERCENT, 'months': SAT_DISCOUNT_MONTHS}
        elif ctx['is_ielts']:
            whatsapp_text = _(
                'Hello! I took the %(test)s on the Academor website (%(score)s). '
                'I would like to join IELTS lessons with the %(percent)s%% discount.'
            ) % {'test': ctx['exam_title'], 'score': result.level, 'percent': IELTS_DISCOUNT_PERCENT}
        else:
            whatsapp_text = _(
                'Hello! I took the %(test)s on the Academor website (%(score)s). '
                'I would like to talk about IELTS preparation.'
            ) % {'test': ctx['exam_title'], 'score': result.level}
        story_rows = []
        for row in rows:
            if row.get('band_label'):
                value = row['band_label']
                sub = f"{_('Band')} · {row['correct']}/{row['total']} {_('correct answers')}"
            else:
                value = f"{row['correct']}/{row['total']}"
                sub = _('correct answers')
                if row.get('scaled'):
                    sub += f" · {row['scaled']}/800"
            story_rows.append({'label': row.get('label') or '', 'value': value, 'sub': sub})
        story = {
            'kicker': _('Score report'),
            'name': result.first_name,
            'test': ctx['exam_title'],
            'date': result.created_at.strftime('%d.%m.%Y'),
            'rows': story_rows,
            'total_label': _('Estimated SAT score') if ctx.get('sat_total') else '',
            'total': f"{ctx['sat_total']} / 1600" if ctx.get('sat_total') else '',
            'cta': _('Check your level too'),
            'site': f"{request.get_host()}/tests",
            'logo': static('portals/img/new_logo.webp'),
            'art': static(STORY_ART),
            'filename': 'academor-result.png',
        }
        ctx.update({
            'story': story,
            'result': result,
            'result_rows': rows,
            'whatsapp_text': whatsapp_text,
            'page_title': f"{ctx['exam_title']} | Academor",
            'page_description': ctx['exam_title'],
        })
        return render(request, self.template_name, ctx)
