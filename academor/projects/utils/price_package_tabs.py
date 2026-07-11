"""Payment tab grouping for course price packages."""

from django.utils.translation import gettext_lazy as _
from django.utils.translation import override

from projects.models import CoursePricePackage

PACKAGE_TAB_ALL = 'all'

PACKAGE_TAB_ORDER = [
    CoursePricePackage.PackageTab.GROUP_STANDARD,
    CoursePricePackage.PackageTab.GROUP_INTENSIVE,
    CoursePricePackage.PackageTab.INDIVIDUAL_STANDARD,
    CoursePricePackage.PackageTab.INDIVIDUAL_INTENSIVE,
    CoursePricePackage.PackageTab.FULL_PACKAGE_GROUP,
    CoursePricePackage.PackageTab.FULL_PACKAGE_INDIVIDUAL,
    CoursePricePackage.PackageTab.FULL_PACKAGE_INSTALLMENT,
    CoursePricePackage.PackageTab.MOCK_TEST,
]

PACKAGE_TAB_ICONS = {
    PACKAGE_TAB_ALL: 'fas fa-th-large',
    CoursePricePackage.PackageTab.GROUP_STANDARD: 'fas fa-users',
    CoursePricePackage.PackageTab.GROUP_INTENSIVE: 'fas fa-bolt',
    CoursePricePackage.PackageTab.INDIVIDUAL_STANDARD: 'fas fa-user',
    CoursePricePackage.PackageTab.INDIVIDUAL_INTENSIVE: 'fas fa-user-plus',
    CoursePricePackage.PackageTab.FULL_PACKAGE_GROUP: 'fas fa-object-group',
    CoursePricePackage.PackageTab.FULL_PACKAGE_INDIVIDUAL: 'fas fa-user-check',
    CoursePricePackage.PackageTab.FULL_PACKAGE_INSTALLMENT: 'fas fa-credit-card',
    CoursePricePackage.PackageTab.MOCK_TEST: 'fas fa-clipboard-list',
}

PACKAGE_TAB_LABELS = {
    PACKAGE_TAB_ALL: _('All'),
    CoursePricePackage.PackageTab.GROUP_STANDARD: _('Group lessons — Standard'),
    CoursePricePackage.PackageTab.GROUP_INTENSIVE: _('Group lessons — Intensive'),
    CoursePricePackage.PackageTab.INDIVIDUAL_STANDARD: _('Individual lessons — Standard'),
    CoursePricePackage.PackageTab.INDIVIDUAL_INTENSIVE: _('Individual lessons — Intensive'),
    CoursePricePackage.PackageTab.FULL_PACKAGE_GROUP: _('Full package — Group'),
    CoursePricePackage.PackageTab.FULL_PACKAGE_INDIVIDUAL: _('Full package — Individual'),
    CoursePricePackage.PackageTab.FULL_PACKAGE_INSTALLMENT: _('Full package — Installments'),
    CoursePricePackage.PackageTab.MOCK_TEST: _('Mock Test'),
}


def package_tab_label(tab_key, lang=None):
    label = PACKAGE_TAB_LABELS.get(tab_key, tab_key)
    if lang:
        with override(lang):
            return str(label)
    return str(label)


def package_tab_icon(tab_key):
    return PACKAGE_TAB_ICONS.get(tab_key, 'fa fa-tag')


def is_valid_package_tab(tab_key):
    return tab_key in PACKAGE_TAB_LABELS


def _package_tab_value(package):
    if isinstance(package, dict):
        return package.get('package_tab') or CoursePricePackage.PackageTab.GROUP_STANDARD
    return (
        getattr(package, 'package_tab', None)
        or CoursePricePackage.PackageTab.GROUP_STANDARD
    )


def filter_packages_for_tab(packages, tab_key):
    if tab_key == PACKAGE_TAB_ALL:
        return list(packages)
    return [pkg for pkg in packages if _package_tab_value(pkg) == tab_key]


def tabs_with_packages(packages):
    present = {_package_tab_value(pkg) for pkg in packages}
    return [tab for tab in PACKAGE_TAB_ORDER if tab in present]


def available_payment_tab_keys(packages):
    if not packages:
        return []
    return [PACKAGE_TAB_ALL, *tabs_with_packages(packages)]


def get_payment_tabs_context(packages, lang=None):
    if not packages:
        return []

    counts = {tab: 0 for tab in PACKAGE_TAB_ORDER}
    for pkg in packages:
        tab = _package_tab_value(pkg)
        if tab in counts:
            counts[tab] += 1

    tabs = [
        {
            'key': PACKAGE_TAB_ALL,
            'label': package_tab_label(PACKAGE_TAB_ALL, lang=lang),
            'icon': package_tab_icon(PACKAGE_TAB_ALL),
            'count': len(packages),
        },
    ]
    tabs.extend([
        {
            'key': tab,
            'label': package_tab_label(tab, lang=lang),
            'icon': package_tab_icon(tab),
            'count': counts[tab],
        }
        for tab in PACKAGE_TAB_ORDER
        if counts[tab] > 0
    ])
    return tabs


def resolve_initial_payment_tab(packages, preferred_package_id=None):
    if not packages:
        return PACKAGE_TAB_ALL

    if preferred_package_id is not None:
        try:
            pkg_id = int(preferred_package_id)
        except (TypeError, ValueError):
            pkg_id = None
        if pkg_id is not None:
            for pkg in packages:
                candidate_id = (
                    pkg.get('id') if isinstance(pkg, dict) else getattr(pkg, 'pk', None)
                )
                if candidate_id == pkg_id:
                    tab = _package_tab_value(pkg)
                    available = available_payment_tab_keys(packages)
    return PACKAGE_TAB_ALL


def build_payment_tab_panels(packages, lang=None, preferred_package_id=None):
    """Pre-rendered tab panels for client-side switching (no AJAX)."""
    from payments.catalog import default_price_package_index

    tabs = get_payment_tabs_context(packages, lang=lang)
    default_tab = resolve_initial_payment_tab(packages, preferred_package_id)
    panels = []

    for tab in tabs:
        tab_packages = filter_packages_for_tab(packages, tab['key'])
        is_active = tab['key'] == default_tab
        panels.append({
            'key': tab['key'],
            'label': tab['label'],
            'icon': tab['icon'],
            'count': tab['count'],
            'packages': tab_packages,
            'is_active': is_active,
            'default_index': default_price_package_index(
                tab_packages,
                preferred_package_id if is_active else None,
            ),
        })

    return panels, default_tab
