from django.views import View
from django.shortcuts import render, redirect
from django.http import Http404
from django.contrib import messages
from django.utils.translation import gettext as _

from projects.forms.forms_v1 import TestUserForm
from projects.models import Option, UserResult
from projects.utils.queries import (
    get_language_from_request,
    get_project_categories,
    serialize_project_category,
    get_tests,
    get_test_by_id,
    serialize_test_for_taking,
    get_background_image,
)
from projects.utils.test_scoring import calculate_level


class TestListPageView(View):
    template_name = 'tests.html'

    def get(self, request):
        lang = get_language_from_request(request)
        tests = get_tests(is_active=True)
        categories = get_project_categories(lang)
        context = {
            'tests': tests,
            'categories': [serialize_project_category(c, lang) for c in categories],
            'language': lang,
            'background_image': get_background_image('about'),
            'footer_image': get_background_image('footer'),
        }
        return render(request, self.template_name, context)


class TestTakePageView(View):
    template_name = 'test-take.html'

    def get(self, request, test_id: int):
        lang = get_language_from_request(request)
        test = get_test_by_id(test_id, is_active=True)
        if not test:
            raise Http404(_("Test not found"))
        categories = get_project_categories(lang)
        context = {
            'test': serialize_test_for_taking(test),
            'user_form': TestUserForm(),
            'categories': [serialize_project_category(c, lang) for c in categories],
            'language': lang,
            'background_image': get_background_image('about'),
            'footer_image': get_background_image('footer'),
        }
        return render(request, self.template_name, context)

    def post(self, request, test_id: int):
        lang = get_language_from_request(request)
        test = get_test_by_id(test_id, is_active=True)
        if not test:
            raise Http404(_("Test not found"))

        user_form = TestUserForm(request.POST)
        if not user_form.is_valid():
            messages.error(request, _('Formda xəta var. Zəhmət olmasa düzəldin.'))
            categories = get_project_categories(lang)
            return render(request, self.template_name, {
                'test': serialize_test_for_taking(test),
                'user_form': user_form,
                'categories': [serialize_project_category(c, lang) for c in categories],
                'language': lang,
                'background_image': get_background_image('about'),
                'footer_image': get_background_image('footer'),
            })
        user_data = user_form.cleaned_data

        # answers: q_<question_id> = <option_id>
        score = 0
        total = test.questions.count()
        for q in test.questions.all():
            selected = request.POST.get(f'q_{q.id}')
            if not selected:
                continue
            try:
                opt = Option.objects.get(id=int(selected), question=q)
            except Exception:
                continue
            if opt.is_correct:
                score += 1

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
        return redirect('projects:test-result', result_id=result.id)


class TestResultPageView(View):
    template_name = 'test-result.html'

    def get(self, request, result_id: int):
        lang = get_language_from_request(request)
        try:
            result = UserResult.objects.select_related('test').get(id=result_id)
        except UserResult.DoesNotExist:
            raise Http404(_("Result not found"))

        categories = get_project_categories(lang)
        context = {
            'result': result,
            'categories': [serialize_project_category(c, lang) for c in categories],
            'language': lang,
            'background_image': get_background_image('about'),
            'footer_image': get_background_image('footer'),
        }
        return render(request, self.template_name, context)

