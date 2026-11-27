from django.views import View
from django.shortcuts import render
from django.http import Http404
from django.contrib import messages
from django.templatetags.static import static
from django.utils.translation import gettext as _

from projects.forms.forms_v1 import TestUserForm
from projects.models import UserResult
from projects.utils.queries import (
    get_language_from_request,
    get_project_categories,
    serialize_project_category,
    get_tests,
    get_test_by_id,
    serialize_test_for_taking,
    serialize_test_for_list,
    get_background_image,
    get_test_take_poster_image,
    get_level_test_taker_count,
)
from projects.utils.cefr import (
    CEFR_LEVELS,
    LEVEL_TEST_DISCOUNT_PERCENT,
    cefr_scale,
    level_test_offer_track,
    level_test_takers_label,
)
from projects.utils.seo_text import meta_plain_excerpt
from projects.utils.test_scoring import calculate_level
from projects.views.level_exam_views import STORY_ART, LevelExamIntroView, exam_test_cards, is_exam_test


def _selected_option_ids_from_post(post, test):
    selected = {}
    for question in test.questions.all():
        raw = post.get(f'q_{question.id}')
        if not raw:
            continue
        try:
            selected[question.id] = int(raw)
        except (TypeError, ValueError):
            continue
    return selected


def _answer_review(test, selected_ids):
    """Each question with the visitor's answer and the right one, for the result page."""
    rows = []
    for number, question in enumerate(test.questions.prefetch_related('options'), start=1):
        options = list(question.options.all())
        chosen = next((o for o in options if o.id == selected_ids.get(question.id)), None)
        right = [o for o in options if o.is_correct]
        if chosen is None:
            status = 'blank'
        elif chosen.is_correct:
            status = 'correct'
        else:
            status = 'wrong'
        rows.append({
            'number': number,
            'text': question.text,
            'chosen': chosen.text if chosen else '',
            'right': ' / '.join(o.text for o in right),
            'status': status,
        })
    return rows


def _wizard_step_from_post(post, questions):
    total = len(questions)
    if not total:
        return 0
    raw = post.get('test_current_step')
    if raw is not None and str(raw).strip() != '':
        try:
            step = int(raw)
            if 0 <= step < total:
                return step
        except (TypeError, ValueError):
            pass
    last_answered = 0
    for index, question in enumerate(questions):
        if question.get('selected_option_id'):
            last_answered = index
    return last_answered


def _serialize_take_test(lang, test, selected_option_ids=None):
    serialized = serialize_test_for_taking(test, lang)
    if not selected_option_ids:
        return serialized
    for question in serialized['questions']:
        question['selected_option_id'] = selected_option_ids.get(question['id'])
    return serialized


def _take_meta(lang, serialized: dict):
    excerpt = meta_plain_excerpt(serialized.get("description") or "")
    if not excerpt.strip():
        excerpt = _("Interactive English placement / practice test at Academor: %(title)s.") % {
            "title": serialized["title"],
        }
    return {
        "page_title": f'{serialized["title"]} | Academor',
        "page_description": excerpt[:320],
    }


def _categories_ctx(lang):
    categories = get_project_categories(lang)
    return [serialize_project_category(c, lang) for c in categories]


def _take_page_extras():
    return {
        'background_image': get_background_image('tests'),
        'test_poster_image': get_test_take_poster_image(),
    }


class TestListPageView(View):
    template_name = 'tests.html'

    def get(self, request):
        lang = get_language_from_request(request)
        tests_qs = get_tests(is_active=True)
        exam_cards = {card['id']: card for card in exam_test_cards(tests_qs, lang)}
        # one list in the admin order: SAT / IELTS exams and classic English level tests together
        test_cards = []
        for test in tests_qs:
            if test.pk in exam_cards:
                test_cards.append(exam_cards[test.pk])
            else:
                test_cards.append({**serialize_test_for_list(test, lang), 'kind': 'level'})
        exam_tests = [card for card in test_cards if card['kind'] != 'level']
        tests = [card for card in test_cards if card['kind'] == 'level']
        categories = get_project_categories(lang)
        context = {
            'test_cards': test_cards,
            'tests': tests,
            'exam_tests': exam_tests,
            'tests_total': len(test_cards),
            'test_takers': level_test_takers_label(get_level_test_taker_count()),
            'categories': [serialize_project_category(c, lang) for c in categories],
            'language': lang,
            'background_image': get_background_image('tests'),
        }
        return render(request, self.template_name, context)


class TestTakePageView(View):
    template_name = 'test-take.html'

    def get(self, request, test_id: int):
        if is_exam_test(test_id):
            return LevelExamIntroView.as_view()(request, test_id=test_id)
        lang = get_language_from_request(request)
        test = get_test_by_id(test_id, is_active=True)
        if not test:
            raise Http404(_("Test not found"))
        ser = _serialize_take_test(lang, test)
        context = {
            'test': ser,
            'cefr_levels': cefr_scale(),
            'user_form': TestUserForm(),
            'categories': _categories_ctx(lang),
            'language': lang,
            **_take_page_extras(),
            **_take_meta(lang, ser),
        }
        return render(request, self.template_name, context)

    def post(self, request, test_id: int):
        if is_exam_test(test_id):
            return LevelExamIntroView.as_view()(request, test_id=test_id)
        lang = get_language_from_request(request)
        test = get_test_by_id(test_id, is_active=True)
        if not test:
            raise Http404(_("Test not found"))

        user_form = TestUserForm(request.POST)
        if not user_form.is_valid():
            messages.error(request, _('Formda xəta var. Zəhmət olmasa düzəldin.'))
            ser = _serialize_take_test(
                lang,
                test,
                _selected_option_ids_from_post(request.POST, test),
            )
            return render(request, self.template_name, {
                'test': ser,
                'cefr_levels': cefr_scale(),
                'user_form': user_form,
                'test_current_step': _wizard_step_from_post(
                    request.POST,
                    ser.get('questions') or [],
                ),
                'categories': _categories_ctx(lang),
                'language': lang,
                **_take_page_extras(),
                **_take_meta(lang, ser),
            })
        user_data = user_form.cleaned_data

        # answers: q_<question_id> = <option_id>
        selected_ids = _selected_option_ids_from_post(request.POST, test)
        review = _answer_review(test, selected_ids)
        score = sum(1 for row in review if row['status'] == 'correct')
        total = len(review)

        level = calculate_level(score, total)
        result = UserResult.objects.create(
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            number=user_data['number'],
            email=user_data.get('email'),
            test=test,
            score=score,
            level=level,
        )
        total_questions = total
        ser = _serialize_take_test(lang, test)
        offer_track = level_test_offer_track(level)
        if offer_track == 'ielts':
            whatsapp_text = _(
                'Hello! I got %(level)s on the Academor English level test. '
                'I would like to find out about IELTS preparation.'
            ) % {'level': level}
        else:
            whatsapp_text = _(
                'Hello! I got %(level)s on the Academor level test. I would like to book the free '
                'trial lesson and a consultation, and use my %(percent)s%% discount.'
            ) % {'level': level, 'percent': LEVEL_TEST_DISCOUNT_PERCENT}
        current_cefr = next((row for row in cefr_scale(level) if row['is_current']), None)
        level_pct = (
            f'{CEFR_LEVELS.index(level) / (len(CEFR_LEVELS) - 1) * 100:.1f}' if level in CEFR_LEVELS else '0'
        )
        # the same shareable result image as the SAT / IELTS score report
        story = {
            'kicker': _('Level test result'),
            'name': result.first_name,
            'test': ser['title'],
            'date': result.created_at.strftime('%d.%m.%Y'),
            'rows': [{
                'label': _('Your level'),
                'value': level,
                'sub': (
                    f"{current_cefr['name']} · " if current_cefr else ''
                ) + f"{result.score}/{total_questions} {_('correct answers')}",
            }],
            'total_label': '',
            'total': '',
            'cta': _('Check your level too'),
            'site': f"{request.get_host()}/tests",
            'logo': static('portals/img/new_logo.webp'),
            'art': static(STORY_ART),
            'filename': 'academor-level.png',
        }
        return render(request, 'level-test-result.html', {
            'test': ser,
            'result': result,
            'review': review,
            'jump_sections': [{'index': 1, 'label': '', 'items': review}] if review else [],
            'review_counts': {
                'correct': score,
                'wrong': sum(1 for row in review if row['status'] == 'wrong'),
                'blank': sum(1 for row in review if row['status'] == 'blank'),
            },
            'level_pct': level_pct,
            'cefr_codes': CEFR_LEVELS,
            'story': story,
            'total_questions': total_questions,
            'current_cefr': current_cefr,
            'offer_track': offer_track,
            'offer_discount': LEVEL_TEST_DISCOUNT_PERCENT,
            'whatsapp_text': whatsapp_text,
            'language': lang,
            **_take_meta(lang, ser),
        })

