(function () {
    function redirectLegacyPortalLoginQuery() {
        try {
            var params = new URLSearchParams(window.location.search);
            if (params.get('portal_login') !== '1') {
                return false;
            }
            var next = params.get('next') || '';
            var loginUrl = '/portal/login/';
            if (next) {
                loginUrl += '?next=' + encodeURIComponent(next);
            }
            window.location.replace(loginUrl);
            return true;
        } catch (e) {
            return false;
        }
    }

    document.addEventListener('DOMContentLoaded', function () {
        redirectLegacyPortalLoginQuery();
    });
})();
