from django.http import JsonResponse
from django.views import View
from django.shortcuts import render
from django.utils.translation import gettext as _

from projects.models import MockTestResult
from projects.utils.queries import (
    get_language_from_request,
    get_project_categories,
    serialize_project_category,
    get_background_image,
)


def _wants_json(request) -> bool:
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return True
    accept = request.headers.get('Accept') or ''
    return 'application/json' in accept


def _serialize_result(result, lang):
    return {
        'full_name': result.full_name,
        'program': result.program_label(lang),
        'score': str(result.score),
        'rank': result.rank,
    }


def _serialize_top5_row(row, lang):
    return {
        'full_name': row.full_name,
        'program': row.program_label(lang),
        'score': str(row.score),
    }


class MockResultsPageView(View):
    template_name = 'mock-results.html'

    def get(self, request):
        return self._render_page(request)

    def post(self, request):
        lang = get_language_from_request(request)
        code = (request.POST.get('code') or '').strip()
        result, not_found = self._lookup(code)

        if _wants_json(request):
            if result:
                return JsonResponse({
                    'ok': True,
                    'result': _serialize_result(result, lang),
                })
            return JsonResponse({
                'ok': False,
                'error': _('No result found for this code.'),
            })

        return self._render_page(
            request,
            submitted_code=code,
            result=result,
            not_found=not_found,
            lang=lang,
        )

    def _lookup(self, code: str):
        if not code:
            return None, True
        result = MockTestResult.lookup_by_code(code)
        return result, result is None

    def _render_page(
        self,
        request,
        submitted_code='',
        result=None,
        not_found=False,
        lang=None,
    ):
        lang = lang or get_language_from_request(request)
        categories = get_project_categories(lang)
        program_tabs = MockTestResult.visible_program_tabs(lang)
        active_key = program_tabs[0]['key'] if program_tabs else ''
        top5_rows = (
            MockTestResult.top5_for_program(active_key) if active_key else []
        )
        result_data = _serialize_result(result, lang) if result else None
        top5_data = [_serialize_top5_row(row, lang) for row in top5_rows]

        context = {
            'categories': [serialize_project_category(c, lang) for c in categories],
            'language': lang,
            'background_image': get_background_image('tests'),
            'submitted_code': submitted_code or '',
            'result': result_data,
            'not_found': not_found,
            'show_top5': bool(program_tabs),
            'program_tabs': program_tabs,
            'active_program_key': active_key,
            'top5': top5_data,
            'page_title': _('Results') + ' | Academor',
            'page_description': _(
                'Look up your mock test result by phone number or unique code.'
            ),
        }
        return render(request, self.template_name, context)


class MockResultsTop5View(View):
    """AJAX: Top 5 list for a selected training program tab."""

    def get(self, request):
        lang = get_language_from_request(request)
        program_key = (request.GET.get('program') or '').strip()
        tabs = MockTestResult.visible_program_tabs(lang)
        valid_keys = {tab['key'] for tab in tabs}

        if not program_key or program_key not in valid_keys:
            return JsonResponse({
                'ok': False,
                'error': _('Training program not found.'),
                'items': [],
            }, status=404)

        items = [
            _serialize_top5_row(row, lang)
            for row in MockTestResult.top5_for_program(program_key)
        ]
        return JsonResponse({
            'ok': True,
            'program': program_key,
            'items': items,
        })
