"""Custom static storage for production deploys."""

from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class LenientManifestStaticFilesStorage(ManifestStaticFilesStorage):
    """
    Same as ManifestStaticFilesStorage but missing optional url() targets in CSS
    don't abort collectstatic (safer with third-party bundles).
    """

    manifest_strict = False
