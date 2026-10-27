"""Custom static storage for production deploys."""

import logging

from django.contrib.staticfiles.storage import ManifestStaticFilesStorage

logger = logging.getLogger(__name__)


class LenientManifestStaticFilesStorage(ManifestStaticFilesStorage):
    """
    Same as ManifestStaticFilesStorage but missing optional url() targets in CSS
    don't abort collectstatic (safer with third-party bundles).

    ``manifest_strict = False`` only relaxes lookups at runtime. During
    ``collectstatic`` post-processing a CSS/JS reference to a file that does not
    exist (e.g. a vendor ``.woff`` fallback or a ``sourceMappingURL`` .map that
    was never shipped) still raises ValueError and aborts the whole run, so no
    new static files reach STATIC_ROOT. ``url_converter`` below leaves such a
    reference unchanged and logs a warning instead.
    """

    manifest_strict = False

    def url_converter(self, name, hashed_files, template=None):
        converter = super().url_converter(name, hashed_files, template)

        def lenient_converter(matchobj):
            try:
                return converter(matchobj)
            except ValueError as exc:
                logger.warning('collectstatic: kept unresolved reference in %s: %s', name, exc)
                return matchobj.groupdict()['matched']

        return lenient_converter
