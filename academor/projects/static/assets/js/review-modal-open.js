(function () {
    document.addEventListener('DOMContentLoaded', function () {
        var modalEl = document.getElementById('reviewFormModal');
        if (!modalEl || !window.bootstrap || !bootstrap.Modal) {
            return;
        }
        var modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        modal.show();
    });
})();
